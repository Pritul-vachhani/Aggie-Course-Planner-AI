import json
import re
from functools import lru_cache

from app.config import CATALOG_PATH

ENDED_MARKER = "This version has ended; see updated course, below."
GE_PATTERN = re.compile(r"General Education:\s*(.*?)\.(?:\n|$)")


def _clean(text: str) -> str:
    """Scraped text uses non-breaking spaces in places; make them normal."""
    return (text or "").replace("\xa0", " ").strip()


def normalize_code(code: str) -> str:
    return _clean(code).replace(" ", "").lower()


def _parse_ge(details: str) -> list[str]:
    match = GE_PATTERN.search(details or "")
    if not match:
        return []
    return [part.strip() for part in match.group(1).split(";") if part.strip()]


def _to_course(raw: dict, department: str) -> dict:
    """Convert one scraped course into the shape of our Course schema."""
    return {
        "course_code": _clean(raw["code"]),
        "title": _clean(raw["title"]),
        "description": _clean(raw["desc"].replace(ENDED_MARKER, "")),
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