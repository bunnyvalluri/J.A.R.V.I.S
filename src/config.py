"""
config.py — JARVIS Central Configuration Manager
==================================================
Responsibilities:
  - Load .env variables (GEMINI_API_KEY, etc.) via python-dotenv
  - Load and validate config.json with sane defaults from data/ directory
  - Expose typed constants and paths to all modules
"""

from __future__ import annotations

import os
import json
import getpass
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────────────────────
SRC_DIR         = Path(__file__).resolve().parent
BASE_DIR        = SRC_DIR.parent
DATA_DIR        = BASE_DIR / "data"
LOG_DIR         = BASE_DIR / "logs"
WEB_DIR         = BASE_DIR / "web"
STATIC_DIR      = WEB_DIR / "static"
ASSETS_DIR      = BASE_DIR / "assets"
DOCS_DIR        = BASE_DIR / "docs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE       = DATA_DIR / "data.json"
NOTES_FILE      = DATA_DIR / "notes.json"
NOTES_FILE_LEGACY = BASE_DIR / "data.txt"
CONFIG_FILE     = DATA_DIR / "config.json"
SCREENSHOTS_DIR = Path.home() / "Pictures" / "JARVIS_Screenshots"

# ── Load .env ──────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    _ENV_FILE = BASE_DIR / ".env"
    load_dotenv(dotenv_path=_ENV_FILE, override=False)
except ImportError:
    pass

# ── API Keys ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY: Optional[str] = (
    os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
)

# ── Typed Configuration Dataclass ─────────────────────────────────────────────
@dataclass
class AppConfig:
    user_name: str          = field(default_factory=lambda: getpass.getuser().capitalize())
    assistant_name: str     = "JARVIS"
    voice_gender: str       = "male"          # 'male' | 'female'
    speech_rate: int        = 180
    speech_volume: float    = 1.0
    voice_enabled: bool     = True
    default_mode: str       = "hybrid"        # 'hybrid' | 'text' | 'voice'
    weather_city: str       = "auto"
    news_source: str        = "google"        # 'google' | 'bbc' | 'toi'
    browser: str            = "auto"
    llm_enabled: bool       = True
    max_news_headlines: int = 4
    log_level: str          = "INFO"
    web_host: str           = "127.0.0.1"
    web_port: int           = 8000
    web_open_browser: bool  = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "AppConfig":
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**known)

    def validate(self) -> "AppConfig":
        """Clamp and sanitise all fields."""
        self.speech_rate    = max(80, min(300, self.speech_rate))
        self.speech_volume  = max(0.0, min(1.0, self.speech_volume))
        self.voice_gender   = self.voice_gender if self.voice_gender in ("male", "female") else "male"
        self.default_mode   = self.default_mode if self.default_mode in ("hybrid", "text", "voice") else "hybrid"
        self.max_news_headlines = max(1, min(10, self.max_news_headlines))
        return self


def load_config() -> AppConfig:
    """Load configuration from config.json, merge with defaults, validate."""
    if not CONFIG_FILE.exists():
        cfg = AppConfig()
        save_config(cfg)
        return cfg
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        cfg = AppConfig.from_dict(raw)
        return cfg.validate()
    except Exception:
        return AppConfig()


def save_config(cfg: AppConfig) -> bool:
    """Persist configuration to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg.to_dict(), f, indent=4)
        return True
    except Exception as exc:
        print(f"[config] Error saving config: {exc}")
        return False


# ── Singleton ──────────────────────────────────────────────────────────────────
CONFIG: AppConfig = load_config()
