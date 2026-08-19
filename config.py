import os
import json
import getpass
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
NOTES_FILE = BASE_DIR / "data.txt"
CONFIG_FILE = BASE_DIR / "config.json"
SCREENSHOTS_DIR = Path.home() / "Pictures" / "JARVIS_Screenshots"

# Default Configuration
DEFAULT_CONFIG = {
    "user_name": getpass.getuser().capitalize(),
    "assistant_name": "JARVIS",
    "voice_gender": "male",  # 'male' or 'female'
    "speech_rate": 180,
    "speech_volume": 1.0,
    "voice_enabled": True,
    "default_mode": "hybrid",  # 'hybrid', 'text', 'voice'
    "weather_city": "auto",
    "news_source": "google",  # 'google', 'bbc', 'toi'
    "browser": "auto"
}

def load_config():
    """Load configuration from config.json or create with defaults."""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(data)
            return merged
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(cfg):
    """Save configuration to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

CONFIG = load_config()
