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
- Build Command: `pip install -r backend/requirements.txt`
- Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `PYTHON_VERSION=3.11.9`, `FRONTEND_ORIGIN` (allowed sites, separated by commas)

The recommender runs all-MiniLM-L6-v2 through ONNX (fastembed) instead of PyTorch so it fits in the free 512 MB instance.