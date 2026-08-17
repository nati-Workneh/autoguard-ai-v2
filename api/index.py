"""Vercel serverless entry point: re-exports the existing FastAPI app unchanged.

Reuses 06_Production_Interface/backend/main.py as the single source of truth for
routing so local (`uvicorn backend.main:app`) and Vercel deployments never drift.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "06_Production_Interface"))

from backend.main import app  # noqa: E402
