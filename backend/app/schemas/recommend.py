from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.course import Course


class StudentProfile(BaseModel):
    interests: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    completed_courses: List[str] = []
    avoid_courses: List[str] = []
    # Not used by the MVP recommender yet
    major: Optional[str] = None
    remaining_ge: List[str] = []


class RecommendedCourse(BaseModel):
    course: Course
    match_score: float = Field(ge=0, le=100)
    reasons: List[str] = []


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendedCourse]