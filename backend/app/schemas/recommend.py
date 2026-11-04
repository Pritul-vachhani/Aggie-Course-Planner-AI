from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.course import Course
from app.services.catalog import canonical_ge


class StudentProfile(BaseModel):
    interests: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    completed_courses: List[str] = []
    avoid_courses: List[str] = []

    # Filters: leave empty / null to mean "any"
    remaining_ge: List[str] = []
    preferred_units: Optional[int] = Field(default=None, ge=1)
    course_level: Optional[Literal["undergraduate", "lower", "upper", "graduate"]] = None
    subject: Optional[str] = None

    # Not used by the recommender yet
    major: Optional[str] = None

    @field_validator("remaining_ge", "completed_courses", "avoid_courses", mode="before")
    @classmethod
    def null_means_empty(cls, value):
        return [] if value is None else value
    
    @field_validator("remaining_ge")
    @classmethod
    def normalize_ge(cls, values: List[str]) -> List[str]:
        names = []
        for value in values:
            name = canonical_ge(value)
            if name is None:
                raise ValueError(f"Unknown GE category: {value!r}")
            names.append(name)
        return names

    @field_validator("subject")
    @classmethod
    def normalize_subject(cls, value: Optional[str]) -> Optional[str]:
        value = (value or "").strip().upper()
        return value or None


class RecommendedCourse(BaseModel):
    course: Course
    match_score: float = Field(ge=0, le=100)
    reasons: List[str] = []


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendedCourse]