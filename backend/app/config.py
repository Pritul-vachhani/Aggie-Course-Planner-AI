import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# backend/app/config.py -> parents[2] is the repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

# Relative paths are resolved from the repo root
_catalog = Path(os.getenv("CATALOG_PATH", "testing/catalog.json"))
CATALOG_PATH = _catalog if _catalog.is_absolute() else REPO_ROOT / _catalog