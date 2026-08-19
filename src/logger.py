"""
logger.py — JARVIS Structured Logging Infrastructure
======================================================
Provides daily-rotating file logs and colored console logging with unique
session IDs for traceability.
"""

import sys
import logging
import uuid
import datetime
from pathlib import Path

# Setup sys.path to ensure relative imports work
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import LOG_DIR, CONFIG

_SESSION_ID = str(uuid.uuid4())[:8].upper()


def get_session_id() -> str:
    return _SESSION_ID


def _build_logger() -> logging.Logger:
    logger = logging.getLogger("JARVIS")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    # Ensure log directory
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y%m%d")
    log_file = LOG_DIR / f"jarvis_{today}.log"

    # File handler
    try:
        fh = logging.FileHandler(str(log_file), encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh_fmt = logging.Formatter(
            f"[%(asctime)s] [{_SESSION_ID}] [%(levelname)-8s] [%(name)s.%(module)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        fh.setFormatter(fh_fmt)
        logger.addHandler(fh)
    except Exception as exc:
        print(f"[logger] File logger init failed: {exc}")

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    ch.setLevel(level_map.get(getattr(CONFIG, "log_level", "INFO"), logging.INFO))
    ch_fmt = logging.Formatter("[%(levelname)s] %(message)s")
    ch.setFormatter(ch_fmt)
    logger.addHandler(ch)

    return logger


log: logging.Logger = _build_logger()
