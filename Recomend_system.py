import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

#Filtering based on interest phrase and recommender 
class CourseRecommender:
    def __init__(self, data: pd.DataFrame, model_name="all-MiniLM-L6-v2"):
        self.data = data.reset_index(drop=True)
        self.model = SentenceTransformer(model_name)          # loaded once
        text = self.data["title"] + ". " + self.data["description"].fillna("")
        self.embeddings = self.model.encode(text.tolist())    # computed once

    def interest_scores(self, phrase: str):
        phrase_emb = self.model.encode([phrase])              # only per-request work
        sim = cosine_similarity(phrase_emb, self.embeddings)[0]
        return np.clip(sim, 0, 1)

    def recommend(self, interest_phrase: str, units: float,
                  ge_category: list[str], prereqs: list[str], top_n: int = 3):
        score_prereqs = np.array(filter_by_prereqs(self.data, prereqs), dtype=float)
        score_units = np.array(filter_by_units(self.data, units))
        score_interest = self.interest_scores(interest_phrase)
        score_ge = np.array(filter_by_ge(self.data, ge_category)) if ge_category else np.ones(len(self.data))
        final = score_ge * 0.25 + score_interest * 0.3 + score_units * 0.15 + score_prereqs * 0.3

        top_idx = np.argsort(final)[::-1][:top_n]
        return [
            {
                "course_code": self.data.at[i, "course_code"],
                "title": self.data.at[i, "title"],
                "score": float(final[i]),   # numpy float -> plain float for JSON
            }
            for i in top_idx
        ]

#Filtering for GE function
def filter_by_ge(data, categories):
    """Input: A dataframe where each row is a course, and a a list of GE categories 
    Output: List where each index represents a course, 1 means course sadifies GE credit and 0 means the oppisite"""
    if isinstance(categories, str):
        categories = [categories]
    categories = [c.upper() for c in categories]
    templist = []
    for ge_types in data["ge_codes"]:
        matches = sum(c in ge_types for c in categories)
        templist.append(matches / len(categories))   # 0..1
    return templist

#Filtering for prerequisites
course_code_pattern = re.compile(r"\b([A-Z]{3}) ?(\d{1,3})([A-Z]*)\b")

def format_code(subj, num, suffix):
    return f"{subj} {int(num):03d}{suffix}"

def normalize_code(code):
    """Turns codes like "mat 21a" into "MAT 021A" so they match the data"""
    match = course_code_pattern.search(code.upper())
    if match is None:
        return code.upper().strip()
    return format_code(*match.groups())

def can_take(prereq_text, completed):
    """Input: A course's prereq_text and a set of completed course codes
    Output: True if the hard course requirements are met
    Note: ";" = and, "or" = or. Consent/standing/recommended/equivalent clauses are ignored"""
    if not isinstance(prereq_text, str):
        return True
    text = prereq_text.upper()
    # "...; or consent of instructor" makes the whole thing optional
    if re.search(r";\s*OR\b", text):
        return True
    for part in re.split(r"[;.]", text):
        if "RECOMMENDED" in part or "EQUIVALENT" in part:
            continue
        for group in re.split(r"\bAND\b", part):
            if "CONSENT" in group:
                continue
            options = [format_code(*m) for m in course_code_pattern.findall(group)]
            if options and not any(code in completed for code in options):
                return False
    return True

def filter_by_prereqs(data, completed):
    """Input: A dataframe where each row is a course, and a list of courses you have completed
    Output: List where each index representa a course, 1 means you can take the course and 0 means you can't"""
    completed = {normalize_code(code) for code in completed}
    templist = []
    for prereq_text in data["prereq_text"]:
        templist.append(can_take(prereq_text, completed))
    return templist

#Filtering for Units
def filter_by_units(data, preferred_units: int = None, max_diff = 3):
    """Input: A data frame where each row is a course and there is a column called "units_average", 
    and the preferred units (if units = -1 that means any units are ok)"""
    if preferred_units == None:
        return [1] * len(data)
    else:
        templist = []
        for course_units in data["units_average"]:
            if pd.isna(course_units):
                templist.append(0)
                continue
            score = max(0, 1 - abs(course_units - preferred_units) / max_diff)
            templist.append(score)
        return templist