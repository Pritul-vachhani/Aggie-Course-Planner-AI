from app.services.mock_data import MOCK_COURSES

def normalize(code: str) -> str:
    return code.replace(" ", "").lower()

def get_recommendations(profile):
    # TODO(Miles): replace with real filtering + scoring
    excluded = {normalize(c) for c in profile.completed_courses + profile.avoid_courses}
    results = []
    for course in MOCK_COURSES:
        if normalize(course["course_code"]) in excluded:
            continue
        results.append({
            "course": course,
            "match_score": 90 - 5 * len(results),
            "reasons": ["Placeholder — real explanations come from the LLM"],
        })
    return results