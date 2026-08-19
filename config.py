"""
config.py — JARVIS Central Configuration Manager
==================================================
Responsibilities:
  - Load .env variables (GEMINI_API_KEY, etc.) via python-dotenv
  - Load and validate config.json with sane defaults
  - Expose typed constants to all other modules
  - Provide save_config() for runtime config persistence
"""

import os
import json
import getpass
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# ── Load .env FIRST before any other imports that might need API keys ──────────
try:
    from dotenv import load_dotenv
    _ENV_FILE = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=_ENV_FILE, override=False)
except ImportError:
    pass  # python-dotenv optional; fall back to OS environment

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).resolve().parent
DATA_FILE       = BASE_DIR / "data.json"
NOTES_FILE      = BASE_DIR / "notes.json"          # upgraded from data.txt
NOTES_FILE_LEGACY = BASE_DIR / "data.txt"          # for migration
CONFIG_FILE     = BASE_DIR / "config.json"
SCREENSHOTS_DIR = Path.home() / "Pictures" / "JARVIS_Screenshots"
LOG_DIR         = BASE_DIR / "logs"

# ── API Keys (loaded from environment) ─────────────────────────────────────────
GEMINI_API_KEY: Optional[str] = (
    os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
)

# ── Typed Configuration Dataclass ─────────────────────────────────────────────
@dataclass
class AppConfig:
    user_name: str       = field(default_factory=lambda: getpass.getuser().capitalize())
    assistant_name: str  = "JARVIS"
    voice_gender: str    = "male"          # 'male' | 'female'
    speech_rate: int     = 180
    speech_volume: float = 1.0
    voice_enabled: bool  = True
    default_mode: str    = "hybrid"        # 'hybrid' | 'text' | 'voice'
    weather_city: str    = "auto"
    news_source: str     = "google"        # 'google' | 'bbc' | 'toi'
    browser: str         = "auto"
    llm_enabled: bool    = True            # enables Gemini fallback
    max_news_headlines: int = 4
    log_level: str       = "INFO"

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
    """Persist configuration to config.json. Returns True on success."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg.to_dict(), f, indent=4)
        return True
    except Exception as exc:
        print(f"[config] Error saving config: {exc}")
        return False


# ── Module-level singletons ────────────────────────────────────────────────────
CONFIG: AppConfig = load_config()

# Backwards-compat shim — old modules do CONFIG.get("key", default)
# The AppConfig dataclass supports attribute access natively.
# Any module that previously did CONFIG["key"] should use CONFIG.key instead.
