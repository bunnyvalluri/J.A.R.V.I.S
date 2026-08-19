"""
api/index.py — Vercel Serverless Function Entry Point for J.A.R.V.I.S.
=====================================================================
Exports the FastAPI `app` ASGI instance for Vercel's serverless runtime.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Resolve project paths
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import the FastAPI application
from src.jarvis_web import app

# Export for Vercel ASGI runtime
__all__ = ["app"]
