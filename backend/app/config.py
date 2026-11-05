import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# backend/app/config.py -> parents[2] is the repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

LLM_API_KEY = os.getenv("LLM_API_KEY", "")

# One site, or several separated by commas (e.g. localhost and the Vercel site)
FRONTEND_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv("FRONTEND_ORIGIN", "http://localhost:3000").split(",")
    if origin.strip()
]


def _repo_path(env_name: str, default: str) -> Path:
    """Relative paths are resolved from the repo root."""
    path = Path(os.getenv(env_name, default))
    return path if path.is_absolute() else REPO_ROOT / path


# WQ 27 data
CATALOG_PATH = _repo_path("CATALOG_PATH", "clean/schedule_202701.json")
PREREQS_PATH = _repo_path("PREREQS_PATH", "clean/prereqs_202701.json")