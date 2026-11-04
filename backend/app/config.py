import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# backend/app/config.py -> parents[2] is the repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
_frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"),
)
FRONTEND_ORIGINS = [origin.strip() for origin in _frontend_origins.split(",") if origin.strip()]

# Relative paths are resolved from the repo root
_catalog = Path(os.getenv("CATALOG_PATH", "testing/catalog.json"))
CATALOG_PATH = _catalog if _catalog.is_absolute() else REPO_ROOT / _catalog
FRONTEND_STATIC_DIR = Path(
    os.getenv("FRONTEND_STATIC_DIR", str(REPO_ROOT / "frontend" / "out"))
)