import re
import sys
from functools import lru_cache

import numpy as np

from app.config import REPO_ROOT
from app.services.catalog import GE_CATEGORIES, load_catalog, normalize_code

# Miles's model lives at the repo root (Recomend_system.py)
sys.path.append(str(REPO_ROOT))
from Recomend_system import CourseRecommender  # noqa: E402

GE_CODES = {name: code for code, name in GE_CATEGORIES.items()}  # "Arts & Humanities" -> "AH"
UNITS_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)(?:\s*-\s*(\d+(?:\.\d+)?))?$")
LEVELS = {
    "undergraduate": (1, 199),
    "lower": (1, 99),
    "upper": (100, 199),
    "graduate": (200, 999),
}


def _units_range(units: str) -> tuple[float, float] | None:
    """'4' -> (4, 4), '1-5' -> (1, 5), anything else -> None."""
    match = UNITS_PATTERN.match(units)
    if not match:
        return None
    low = float(match.group(1))
    return low, float(match.group(2) or low)


def _units_average(units: str) -> float | None:
    """'4' -> 4.0, '1-5' -> 3.0, anything else -> None."""
    units_range = _units_range(units)
    return sum(units_range) / 2 if units_range else None


def _to_model_data(catalog: dict[str, dict]) -> dict[str, np.ndarray]:
    courses = list(catalog.values())
    ge_codes = np.empty(len(courses), dtype=object)
    ge_codes[:] = [[GE_CODES[name] for name in course["ge_categories"]] for course in courses]
    return {
        "course_code": np.asarray([course["course_code"] for course in courses]),
        "title": np.asarray([course["title"] for course in courses]),
        "description": np.asarray([course["description"] for course in courses]),
        "ge_codes": ge_codes,
        "prereq_text": np.asarray([course["prerequisites"] for course in courses]),
        "units_average": np.asarray([
            average if (average := _units_average(course["units"])) is not None else np.nan
            for course in courses
        ], dtype=np.float32),
    }


@lru_cache(maxsize=1)
def get_model() -> CourseRecommender:
    """Build Miles's model once and embed the catalog for semantic search."""
    return CourseRecommender(_to_model_data(load_catalog()))


def _matches_level(course: dict, level: str | None) -> bool:
    if level is None:
        return True
    parts = course["course_code"].split()
    match = re.match(r"\d+", parts[1]) if len(parts) > 1 else None
    if not match:
        return False
    low, high = LEVELS[level]
    return low <= int(match.group()) <= high


def _meets_filters(course: dict, profile) -> bool:
    """The model only boosts matching courses; this guarantees every
    result actually satisfies the filters the student selected."""
    if profile.remaining_ge and not set(profile.remaining_ge) & set(course["ge_categories"]):
        return False
    if profile.preferred_units is not None:
        units = _units_range(course["units"])
        if units is None or not units[0] <= profile.preferred_units <= units[1]:
            return False
    if profile.subject and not course["course_code"].upper().startswith(profile.subject):
        return False
    return _matches_level(course, profile.course_level)


def _reasons(course: dict, profile) -> list[str]:
    reasons = []
    ge = [name for name in course["ge_categories"] if name in profile.remaining_ge]
    if ge:
        reasons.append(f"Satisfies {', '.join(ge)}")
    if not course["prerequisites"]:
        reasons.append("No prerequisites")
    return reasons


def get_recommendations(profile) -> list[dict]:
    model = get_model()
    ranked = model.recommend(
        interest_phrase=profile.interests,
        units=profile.preferred_units,
        ge_category=[GE_CODES[name] for name in profile.remaining_ge],
        prereqs=profile.completed_courses,
        subject=profile.subject,
        top_n=len(model.data["course_code"]),  # rank everything, then filter below
    )

    catalog = load_catalog()
    excluded = {normalize_code(c) for c in profile.completed_courses + profile.avoid_courses}

    recommendations = []
    for item in ranked:
        key = normalize_code(item["course_code"])
        course = catalog[key]
        if key in excluded or not _meets_filters(course, profile):
            continue
        recommendations.append({
            "course": course,
            "match_score": round(item["score"] * 100, 1),
            "reasons": _reasons(course, profile),
        })
        if len(recommendations) == profile.top_k:
            break
    return recommendations