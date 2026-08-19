"""
logger.py — JARVIS Production Logger
=====================================
Structured rotating file + console logger.
Every session gets a unique ID embedded in every log line.
Logs rotate daily and are retained for 30 days.
"""

import logging
import uuid
import platform
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime

# ── Session Identity ───────────────────────────────────────────────────────────
SESSION_ID: str = str(uuid.uuid4())[:8].upper()

# ── Log Directory ──────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ── Custom Formatter ───────────────────────────────────────────────────────────
class JarvisFormatter(logging.Formatter):
    """Adds session ID and cleaner formatting to every log record."""

    LEVEL_LABELS = {
        "DEBUG":    "DBG",
        "INFO":     "INF",
        "WARNING":  "WRN",
        "ERROR":    "ERR",
        "CRITICAL": "CRT",
    }

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level = self.LEVEL_LABELS.get(record.levelname, record.levelname[:3])
        return (
            f"[{ts}] [{SESSION_ID}] [{level}] "
            f"[{record.module}:{record.lineno}] {record.getMessage()}"
        )


# ── Logger Factory ─────────────────────────────────────────────────────────────
def _build_logger() -> logging.Logger:
    logger = logging.getLogger("jarvis")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger  # Already initialised (e.g. imported twice)

    # File handler — daily rotation, 30 days retention
    log_file = LOG_DIR / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JarvisFormatter())

    logger.addHandler(file_handler)
    return logger


# ── Module-level singleton ─────────────────────────────────────────────────────
log = _build_logger()


def get_session_id() -> str:
    """Return the 8-character uppercase session ID."""
    return SESSION_ID


def get_log_file_path() -> Path:
    """Return the path of today's log file."""
    return LOG_DIR / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
