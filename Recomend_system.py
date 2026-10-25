import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

def filter_interest(phrase, data):
    copy = data.copy()
    model = SentenceTransformer("all-MiniLM-L6-v2") 
    copy["text"] = copy["title"] + ". " + copy["description"].fillna("")
    embeddings = model.encode(copy["text"].tolist(), show_progress_bar=True)
    phrase_emb = model.encode([phrase])
    sim_scores = cosine_similarity(phrase_emb, embeddings)[0]
    score = (sim_scores + 1) / 2
    return score

def filter_by_ge(data, categories):
    if isinstance(categories, str):
        categories = [categories]
    categories = [c.upper() for c in categories]
    templist = []
    for ge_types in data["ge_codes"]:
        matches = sum(c in ge_types for c in categories)
        templist.append(matches / len(categories))   # 0..1
    return templist

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
    Output: Dataframe with only the courses whose prerequisites you have met"""
    completed = {normalize_code(code) for code in completed}
    templist = []
    for prereq_text in data["prereq_text"]:
        templist.append(can_take(prereq_text, completed))
    return templist

def filter_by_units(data, preferred_units: int, max_diff = 3):
    templist = []
    for course_units in data["units_average"]:
        if pd.isna(course_units):
            templist.append(0)
            continue
        score = max(0, 1 - abs(course_units - preferred_units) / max_diff)
        templist.append(score)
    return templist

def filter_courses(data, interest_phrase:str, units:int, ge_category, prereqs:list, top_n = 3):
    data = get_units(data.copy())
    score_prereqs = np.array(filter_by_prereqs(data, prereqs), dtype=float)
    score_units = np.array(filter_by_units(data, units))
    score_interest = np.array(filter_interest(interest_phrase, data))
    score_ge = np.array(filter_by_ge(data, ge_category))
    final_score = score_ge * 0.3 + score_interest * 0.4 + score_units * 0.15 + score_prereqs * 0.15
    top_idx = np.argsort(final_score)[::-1][:top_n]
    return data["course_code"].iloc[top_idx].tolist()