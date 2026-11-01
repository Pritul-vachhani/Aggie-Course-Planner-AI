# claude wrote this

import re
from functools import lru_cache

from app.services.catalog import load_catalog, normalize_code

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "do", "for", "from",
    "if", "in", "into", "is", "it", "like", "love", "me", "my", "of", "on", "or",
    "so", "some", "that", "the", "this", "to", "want", "with", "also", "about",
    "class", "classes", "course", "courses", "interested", "learn", "things",
}

UNITS_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)(?:\s*-\s*(\d+(?:\.\d+)?))?$")
LEVELS = {"lower": (1, 99), "upper": (100, 199), "graduate": (200, 999)}


# ------------------------------------------------------------------
# Step 1: FILTER — hard constraints the student chose. Runs first,
# so the top results always satisfy every filter.
# ------------------------------------------------------------------

def _units_range(units: str) -> tuple[float, float] | None:
    """'4' -> (4, 4), '1-5' -> (1, 5), anything else -> None."""
    match = UNITS_PATTERN.match(units)
    if not match:
        return None
    low = float(match.group(1))
    return low, float(match.group(2) or low)


def _course_number(code: str) -> int | None:
    """'ECS 032A' -> 32"""
    parts = code.split()
    match = re.match(r"\d+", parts[1]) if len(parts) > 1 else None
    return int(match.group()) if match else None


def is_eligible(course: dict, key: str, profile, excluded: set[str]) -> bool:
    if key in excluded:
        return False
    if profile.remaining_ge and not set(profile.remaining_ge) & set(course["ge_categories"]):
        return False
    if profile.preferred_units is not None:
        units = _units_range(course["units"])
        if units is None or not units[0] <= profile.preferred_units <= units[1]:
            return False
    if profile.course_level:
        number = _course_number(course["course_code"])
        low, high = LEVELS[profile.course_level]
        if number is None or not low <= number <= high:
            return False
    if profile.subject and not course["course_code"].upper().startswith(profile.subject):
        return False
    return True


# ------------------------------------------------------------------
# Step 2: RANK — PLACEHOLDER keyword matcher. The embedding model
# replaces score_courses(); everything else stays the same.
# ------------------------------------------------------------------

def _tokens(text: str) -> set[str]:
    return {
        w for w in re.findall(r"[a-z]+", text.lower())
        if len(w) > 1 and w not in STOPWORDS
    }


@lru_cache(maxsize=1)
def _course_tokens() -> dict[str, tuple[set[str], set[str]]]:
    return {
        key: (_tokens(c["title"]), _tokens(c["description"]))
        for key, c in load_catalog().items()
    }


def score_courses(interests: str, candidates: list[str]) -> list[tuple[str, float, list[str]]]:
    """Rank candidate courses. Returns (course_key, score 0-100, matched words), best first."""
    wanted = _tokens(interests)
    if not wanted:
        return []

    tokens = _course_tokens()
    scored = []
    for key in candidates:
        title_words, desc_words = tokens[key]
        matched = wanted & (title_words | desc_words)
        if matched:
            score = 100 * len(matched) / len(wanted)
            title_hits = len(wanted & title_words)  # tie-breaker
            scored.append((key, score, title_hits, sorted(matched)))

    scored.sort(key=lambda r: (r[1], r[2]), reverse=True)
    return [(key, score, matched) for key, score, _, matched in scored]


def get_recommendations(profile) -> list[dict]:
    catalog = load_catalog()
    excluded = {normalize_code(c) for c in profile.completed_courses + profile.avoid_courses}
    candidates = [key for key, course in catalog.items() if is_eligible(course, key, profile, excluded)]

    recommendations, used = [], set()
    for key, score, matched in score_courses(profile.interests, candidates):
        if len(recommendations) == profile.top_k:
            break
        recommendations.append({
            "course": catalog[key],
            "match_score": round(score, 1),
            "reasons": [f"Matches your interest in: {', '.join(matched)}"],
        })
        used.add(key)

    # Not enough interest matches: if the student picked filters, fill up
    # with courses that still meet all of them
    has_filters = bool(
        profile.remaining_ge or profile.preferred_units or profile.course_level or profile.subject
    )
    for key in candidates if has_filters else []:
        if len(recommendations) == profile.top_k:
            break
        if key not in used:
            recommendations.append({
                "course": catalog[key],
                "match_score": 0.0,
                "reasons": ["Meets your filters, but didn't match your interests"],
            })
    return recommendations