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

## Deployment CORS
Vercel production and preview domains ending in `.vercel.app` are allowed automatically. If the frontend uses a custom domain, set `FRONTEND_ORIGIN` on the backend to that exact origin (scheme and hostname, with no trailing slash), then redeploy the backend.