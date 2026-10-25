import re
from functools import lru_cache

from app.services.catalog import load_catalog, normalize_code

# ------------------------------------------------------------------
# PLACEHOLDER keyword matcher. Miles's TF-IDF module replaces
# score_courses(); get_recommendations() stays the same.
# ------------------------------------------------------------------

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "do", "for", "from",
    "if", "in", "into", "is", "it", "like", "love", "me", "my", "of", "on", "or",
    "so", "some", "that", "the", "this", "to", "want", "with", "also", "about",
    "class", "classes", "course", "courses", "interested", "learn", "things",
}


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


def score_courses(interests: str) -> list[tuple[str, float, list[str]]]:
    """Return (course_key, score 0-100, matched words), best first."""
    wanted = _tokens(interests)
    if not wanted:
        return []

    scored = []
    for key, (title_words, desc_words) in _course_tokens().items():
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

    recommendations = []
    for key, score, matched in score_courses(profile.interests):
        if key in excluded:
            continue
        recommendations.append({
            "course": catalog[key],
            "match_score": round(score, 1),
            "reasons": [f"Matches your interest in: {', '.join(matched)}"],
        })
        if len(recommendations) == profile.top_k:
            break
    return recommendations