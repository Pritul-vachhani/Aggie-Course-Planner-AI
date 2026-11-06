from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import FRONTEND_ORIGINS
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
    allow_origin_regex=r"https://([a-zA-Z0-9-]+)\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses.router)
app.include_router(recommend.router)

@app.get("/")
def root():
    return {"status": "running"}