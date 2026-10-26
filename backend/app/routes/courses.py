from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.schemas.course import Course
from app.services.catalog import load_catalog, get_course

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=List[Course])
def list_courses(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    courses = list(load_catalog().values())
    return courses[offset: offset + limit]


@router.get("/{course_code}", response_model=Course)
def read_course(course_code: str):
    course = get_course(course_code)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course