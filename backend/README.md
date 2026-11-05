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

## Deploy (Render)
- Build Command: `pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r backend/requirements.txt`
- Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `PYTHON_VERSION=3.11.9`, `FRONTEND_ORIGIN` (allowed sites, separated by commas)

PyTorch is installed separately from the CPU-only index so the build doesn't pull in GPU libraries.