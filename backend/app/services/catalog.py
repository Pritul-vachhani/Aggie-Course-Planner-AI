import json
import re
from functools import lru_cache

from app.config import CATALOG_PATH, PREREQS_PATH

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

CODE_PATTERN = re.compile(r"^([A-Za-z]+)(\d+)([A-Za-z]*)$")


def _clean(text: str | None) -> str:
    """Scraped text uses non-breaking spaces in places; make them normal."""
    return (text or "").replace("\xa0", " ").strip()


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


def _format_units(low: float, high: float) -> str:
    """(4, 4) -> '4', (1, 5) -> '1-5', (4.5, 4.5) -> '4.5'."""
    return f"{low:g}" if low == high else f"{low:g}-{high:g}"


def _details(raw: dict, ge_names: list[str]) -> str:
    """Extra info shown under "Course details" on the frontend."""
    parts = []
    if ge_names:
        parts.append(f"General Education: {', '.join(ge_names)}.")
    if raw.get("cross_listings"):
        parts.append(f"Cross-listed with {', '.join(raw['cross_listings'])}.")
    if raw.get("credit_limit_text"):
        parts.append(_clean(raw["credit_limit_text"]))
    return " ".join(parts)


def _to_course(raw: dict, sections: list[dict], department: str, prereqs: str | None) -> dict:
    """Convert one course from Jeremy's schedule into the shape of our Course schema."""
    ge_names = [GE_CATEGORIES[code] for code in raw.get("ge_codes", []) if code in GE_CATEGORIES]
    return {
        "course_code": _clean(raw["course_code"]),
        "title": _clean(raw["title"]),
        "description": _clean(raw.get("description")),
        "details": _details(raw, ge_names),
        "units": _format_units(
            min(s["units_min"] for s in sections),
            max(s["units_max"] for s in sections),
        ),
        "prerequisites": _clean(prereqs).rstrip("."),
        "ge_categories": ge_names,
        "department": _clean(department),
    }


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, dict]:
    """Load the Winter 2027 schedule once and index it by normalized course code.

    Courses whose sections are all placeholders (special study, internships,
    research units arranged with a department) aren't open for regular
    enrollment, so they're left out.
    """
    with open(CATALOG_PATH, encoding="utf-8") as f:
        schedule = json.load(f)
    with open(PREREQS_PATH, encoding="utf-8") as f:
        prereqs = json.load(f)

    catalog: dict[str, dict] = {}
    for subject in schedule.values():
        for raw in subject["courses"].values():
            sections = [s for s in raw["sections"].values() if not s["is_placeholder"]]
            if not sections:
                continue
            code = _clean(raw["course_code"])
            # Prerequisites in effect for Winter 2027; fall back to the schedule's own text
            prereq = prereqs.get(code) or raw.get("prereq_text")
            course = _to_course(raw, sections, subject["name"], prereq)
            catalog[normalize_code(code)] = course
    return catalog


def get_course(code: str) -> dict | None:
    return load_catalog().get(normalize_code(code))