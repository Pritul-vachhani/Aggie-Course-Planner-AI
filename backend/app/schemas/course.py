from typing import List
from pydantic import BaseModel

class Course(BaseModel):
    course_code: str
    title: str
    description: str
    units: int
    prerequisites: List[str] = []
    ge_categories: List[str] = []
    department: str