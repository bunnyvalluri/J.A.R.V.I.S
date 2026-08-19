"""
diction.py — Offline Dictionary Lookup Service
"""

import sys
import json
from difflib import get_close_matches
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import DATA_FILE

try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    data = {}


def translate(word: str) -> str:
    word = word.lower().strip()
    if word in data:
        res = data[word]
        return "; ".join(res) if isinstance(res, list) else str(res)
    elif len(get_close_matches(word, data.keys())) > 0:
        match = get_close_matches(word, data.keys())[0]
        res = data[match]
        val = "; ".join(res) if isinstance(res, list) else str(res)
        return f"Did you mean {match} instead? Meaning: {val}"
    else:
        return "Word not found in local dictionary."
