FROM node:22-bookworm-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ARG NEXT_PUBLIC_API_BASE_URL=/api
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    CATALOG_PATH=/app/testing/catalog.json \
    FRONTEND_STATIC_DIR=/app/frontend/out \
    EMBEDDING_MODEL_PATH=/opt/models/all-MiniLM-L6-v2 \
    COURSE_EMBEDDINGS_PATH=/opt/models/all-MiniLM-L6-v2/course-embeddings.npy

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY Recomend_system.py ./
COPY testing/catalog.json ./testing/catalog.json
RUN python -c "from Recomend_system import OnnxSentenceEncoder; OnnxSentenceEncoder('sentence-transformers/all-MiniLM-L6-v2')"
RUN python -m app.services.build_embeddings
COPY --from=frontend-build /app/frontend/out ./frontend/out

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
