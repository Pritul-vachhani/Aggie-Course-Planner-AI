import os
from pathlib import Path
from urllib.request import urlretrieve

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
import re


class OnnxSentenceEncoder:
    def __init__(self, model_name: str):
        model_dir = Path(
            os.getenv(
                "EMBEDDING_MODEL_PATH",
                str(Path.home() / ".cache" / "aggie-course-planner" / "all-MiniLM-L6-v2"),
            )
        )
        tokenizer_path = model_dir / "tokenizer.json"
        onnx_path = model_dir / "onnx" / "model.onnx"
        files = {
            "tokenizer.json": tokenizer_path,
            "onnx/model.onnx": onnx_path,
        }
        for filename, destination in files.items():
            if not destination.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                temporary_path = destination.with_suffix(destination.suffix + ".tmp")
                url = f"https://huggingface.co/{model_name}/resolve/main/{filename}"
                urlretrieve(url, temporary_path)
                temporary_path.replace(destination)

        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.tokenizer.enable_truncation(max_length=256)
        self.tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")

        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(
            str(onnx_path),
            sess_options=options,
            providers=["CPUExecutionProvider"],
        )
        self.input_names = {item.name for item in self.session.get_inputs()}

    def encode(self, sentences: list[str], batch_size: int = 32) -> np.ndarray:
        embeddings = []
        for start in range(0, len(sentences), batch_size):
            encodings = self.tokenizer.encode_batch(sentences[start : start + batch_size])
            batch = {
                "input_ids": np.asarray([encoding.ids for encoding in encodings], dtype=np.int64),
                "attention_mask": np.asarray(
                    [encoding.attention_mask for encoding in encodings], dtype=np.int64
                ),
                "token_type_ids": np.asarray(
                    [encoding.type_ids for encoding in encodings], dtype=np.int64
                ),
            }
            inputs = {
                name: batch[name]
                for name in self.input_names
                if name in batch
            }
            token_embeddings = self.session.run(None, inputs)[0]
            mask = batch["attention_mask"][:, :, np.newaxis].astype(np.float32)
            pooled = (token_embeddings * mask).sum(axis=1) / np.maximum(mask.sum(axis=1), 1)
            embeddings.append(pooled)

        return np.concatenate(embeddings) if embeddings else np.empty((0, 384), dtype=np.float32)


class CourseRecommender:
    def __init__(self, data: dict, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the encoder and load or compute course embeddings."""
        self.data = data
        self.model = OnnxSentenceEncoder(model_name)
        embeddings_path = os.getenv("COURSE_EMBEDDINGS_PATH")
        if embeddings_path:
            self.embeddings = np.load(embeddings_path, mmap_mode="r")
            expected_shape = (len(self.data["course_code"]), 384)
            if self.embeddings.shape != expected_shape:
                raise ValueError(
                    f"Course embeddings have shape {self.embeddings.shape}; expected {expected_shape}."
                )
        else:
            text = [
                f"{title}. {description or ''}"
                for title, description in zip(self.data["title"], self.data["description"])
            ]
            self.embeddings = self.model.encode(text)

    def interest_scores(self, phrase: str):
        """Input: An interest phrase
        Output: A list of values from one to zero with one meaning it is close to the phrase. Each value reperest a class
        Note: Don't use this fucntion, this function is a helper function for recommender"""
        phrase_emb = self.model.encode([phrase])[0]
        denominator = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(phrase_emb)
        sim = np.divide(
            self.embeddings @ phrase_emb,
            denominator,
            out=np.zeros(len(self.embeddings), dtype=np.float32),
            where=denominator != 0,
        )
        return np.clip(sim, 0, 1)
    
    def get_course_level(self, course_level:int):
        """Input: Course data containing each course
        Output: Changes self.data to only have only have right course level
        Note: 0 = Lower Division, 1 = Upper Division, 2 = Graduate Courses, 
        3 = Professional Courses for Teachers and Health Providers, 4 = Professional Graduate Training"""
        mask = np.array([code[4] == str(course_level) for code in self.data["course_code"]])
        self.data = {name: values[mask] for name, values in self.data.items()}
        self.embeddings = self.embeddings[mask]
        
    def recommend(self, interest_phrase: str, units: float,
                  ge_category: list[str], prereqs: list[str], subject:str, top_n: int = 3):
        score_prereqs = np.array(filter_by_prereqs(self.data, prereqs), dtype=float)
        score_units = np.array(filter_by_units(self.data, units))
        score_interest = self.interest_scores(interest_phrase)
        score_subject = np.array(filter_subject(self.data, subject))
        score_ge = (
            np.array(filter_by_ge(self.data, ge_category))
            if ge_category
            else np.ones(len(self.data["course_code"]))
        )
        final = score_ge * 0.2 + score_interest * 0.25 + score_units * 0.2 + score_prereqs * 0.2 + score_subject * 0.15

        top_idx = np.argsort(final)[::-1][:top_n]
        return [
            {
                "course_code": self.data["course_code"][i],
                "title": self.data["title"][i],
                "score": float(final[i]),   
            }
            for i in top_idx
        ]

#Filtering for GE function
def filter_by_ge(data, categories):
    """Input: Course data and a list of GE categories
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
    """Input: Course data and a list of courses you have completed
    Output: List where each index representa a course, 1 means you can take the course and 0 means you can't"""
    completed = {normalize_code(code) for code in completed}
    templist = []
    for prereq_text in data["prereq_text"]:
        templist.append(can_take(prereq_text, completed))
    return templist

#Filter by units
def filter_by_units(data, preferred_units: int = None, max_diff = 3):
    """Input: Course data with a numeric "units_average" column,
    and the preferred units (if units = None that means any units are ok)"""
    if preferred_units == None:
        return [1] * len(data["course_code"])
    else:
        templist = []
        for course_units in data["units_average"]:
            if not np.isfinite(course_units):
                templist.append(0)
                continue
            score = max(0, 1 - abs(course_units - preferred_units) / max_diff)
            templist.append(score)
        return templist

#Filtering for subject
def filter_subject(data, subject:str):
    """Input: Course data containing each course
    Outpu: List where each index representa a course, 1 it has the correct subject and 0 it doesn't"""
    if subject == None:
        return np.ones(len(data["course_code"]))
    else:
        subject = subject.strip().upper()
        templist = []
        for i in data["course_code"]:
            if i[:3] in subject:
                templist.append(1)
            else:
                templist.append(0)
        return templist