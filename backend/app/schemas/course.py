from typing import List
from pydantic import BaseModel


class Course(BaseModel):
    course_code: str
    title: str
    description: str
    units: str                    # "4", or a range like "1-5"
    prerequisites: str = ""       # raw catalog text, can contain "or"
    ge_categories: List[str] = []
    department: str