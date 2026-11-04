import json
import re
from functools import lru_cache

from app.config import CATALOG_PATH

ENDED_MARKER = "This version has ended; see updated course, below."
GE_PATTERN = re.compile(r"General Education:\s*(.*?)\.(?:\n|$)")

# GE categories, keyed by catalog abbreviation
GE_CATEGORIES = {
    "AH": "Arts & Humanities",
    "SE": "Science & Engineering",
    "SS": "Social Sciences",
    "WE": "Writing Experience",
    "WC": "World Cultures",
    "VL": "Visual Literacy",
    "OL": "Oral Skills",
    "SL": "Scientific Literacy",
    "QL": "Quantitative Literacy",
    "DD": "Domestic Diversity",
    "ACGH": "American Cultures, Governance, & History",
}

def _clean(text: str) -> str:
    """Scraped text uses non-breaking spaces in places; make them normal."""
    return (text or "").replace("\xa0", " ").strip()


CODE_PATTERN = re.compile(r"^([A-Za-z]+)(\d+)([A-Za-z]*)$")


def normalize_code(code: str) -> str:
    """'ECS 32a', 'ecs032A' and 'ECS 032A' all become 'ecs032a'."""
    compact = _clean(code).replace(" ", "")
    match = CODE_PATTERN.match(compact)
    if not match:
        return compact.lower()
    subject, number, suffix = match.groups()
    return f"{subject}{int(number):03d}{suffix}".lower()


def canonical_ge(label: str) -> str | None:
    """Map 'AH', 'Arts & Humanities' or 'Arts & Humanities (AH)' to 'Arts & Humanities'."""
    text = _clean(label)
    for code, name in GE_CATEGORIES.items():
        if text.upper() == code or name.lower() in text.lower() or f"({code})" in text.upper():
            return name
    return None


def _parse_ge(details: str) -> list[str]:
    match = GE_PATTERN.search(details or "")
    if not match:
        return []
    text = match.group(1)
    return [
        name for code, name in GE_CATEGORIES.items()
        if name in text or f"({code})" in text
    ]


def _to_course(raw: dict, department: str) -> dict:
    """Convert one scraped course into the shape of our Course schema."""
    return {
        "course_code": _clean(raw["code"]),
        "title": _clean(raw["title"]),
        "description": _clean(raw["desc"].replace(ENDED_MARKER, "")),
        "details": _clean(raw.get("details", "")),
        "units": _clean(raw["units"]),
        "prerequisites": _clean(raw["prereqs"]).rstrip("."),
        "ge_categories": _parse_ge(_clean(raw.get("details", ""))),
        "department": department,
    }


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, dict]:
    """Load the catalog once and index it by normalized course code."""
    with open(CATALOG_PATH, encoding="utf-8") as f:
        subjects = json.load(f)

    catalog: dict[str, dict] = {}
    for subject in subjects:
        for raw in subject["courses"]:
            course = _to_course(raw, subject["subj"])
            key = normalize_code(course["course_code"])
            if key in catalog and ENDED_MARKER in raw["desc"]:
                continue  # keep the current version over an ended one
            catalog[key] = course
    return catalog


def get_course(code: str) -> dict | None:
    return load_catalog().get(normalize_code(code))