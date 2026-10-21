from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.course import Course
from app.services.mock_data import MOCK_COURSES

router = APIRouter(prefix="/courses", tags=["courses"])

def normalize(code: str) -> str:
    return code.replace(" ", "").lower()

@router.get("/", response_model=List[Course])
def get_courses():
    return MOCK_COURSES

@router.get("/{course_code}", response_model=Course)
def get_course(course_code: str):
    for course in MOCK_COURSES:
        if normalize(course["course_code"]) == normalize(course_code):
            return course
    raise HTTPException(status_code=404, detail="Course not found")