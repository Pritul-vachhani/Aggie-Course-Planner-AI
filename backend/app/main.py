from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import FRONTEND_ORIGINS, FRONTEND_STATIC_DIR
from app.routes import courses, recommend
from app.services.recommender import get_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_model()  # load the model and embed the catalog before accepting requests
    yield


app = FastAPI(title="AggieAI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses.router)
app.include_router(courses.router, prefix="/api")
app.include_router(recommend.router)
app.include_router(recommend.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


if FRONTEND_STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_STATIC_DIR, html=True), name="frontend")