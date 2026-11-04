# Free public demo deployment

The project can be deployed as one Docker web service on Render. The service builds the Next.js frontend as static files, serves them from FastAPI, and exposes the course and recommendation APIs from the same public URL.

The Docker build uses the CPU ONNX version of the existing MiniLM embedding model and precomputes the course vectors into the image. This avoids installing PyTorch and rebuilding all course embeddings whenever the free service wakes.

## Deploy with Render

1. Push the project to a GitHub repository.
2. Sign in to [Render](https://render.com), choose **New → Blueprint**, and connect the repository.
3. Keep `render.yaml` at the repository root and create the `aggie-course-planner` service on the **Free** plan.
4. Wait for the Docker build and first startup to finish. Render shows the public `onrender.com` URL on the service page.
5. Open that URL to use the app. Check `/health` for service status and `/api/courses/?limit=1` to verify the API.

The Docker image contains the course catalog, so the deployed service does not depend on a local file or a separate database. Frontend API requests use the same origin as the UI.

## Free-tier behavior

Render's free web services sleep after 15 minutes without traffic and wake when a new request arrives. The first request after sleep can take around a minute while the service starts and loads the model. The free instance-hours allowance is shared across services in the Render workspace. This is suitable for a class/project demo, but not a production availability guarantee.

## Run locally

Start the backend from the repository root:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload
```

In another terminal:

```powershell
Set-Location frontend
npm ci
npm run dev
```

The frontend defaults to `http://localhost:8000` for its API. To override that, set `NEXT_PUBLIC_API_BASE_URL`; for the deployed, same-origin build it is set to `/api`.
