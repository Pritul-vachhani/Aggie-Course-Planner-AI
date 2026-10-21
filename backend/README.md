# AggieAI Backend (FastAPI)

## Run locally
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

API docs: http://localhost:8000/docs

## Endpoints
- GET  /courses/          — all courses
- GET  /courses/{code}    — one course
- POST /recommend/        — ranked recommendations from a student profile

## Setup
Copy `.env.example` to `.env` and fill in values.