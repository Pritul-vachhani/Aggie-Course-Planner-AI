from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.course import Course

class StudentProfile(BaseModel):
    query: Optional[str] = None
    major: Optional[str] = None
    completed_courses: List[str] = []
    remaining_ge: List[str] = []
    interests: List[str] = []
    preferred_units: Optional[int] = None
    avoid_courses: List[str] = []

class RecommendedCourse(BaseModel):
    course: Course
    match_score: float = Field(ge=0, le=100)
    reasons: List[str]

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendedCourse]