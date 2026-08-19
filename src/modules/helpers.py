"""
helpers.py — JARVIS Utility Functions
=======================================
Command capture (voice + text), persistent notes (JSON with timestamps),
dictionary lookup, jokes, and system shortcuts.
"""

import sys
import json
import datetime
import pyjokes
try:
    import speech_recognition as sr
except Exception:
    sr = None
from difflib import get_close_matches
from pathlib import Path

# Ensure src in sys.path
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.voice_engine import speak, voice
from services.weather_service import get_weather
from services.system_control import get_system_stats, take_screenshot, change_volume, lock_screen, get_time_and_date
from config import DATA_FILE, NOTES_FILE, NOTES_FILE_LEGACY
from ui import (
    print_listening, print_recognizing, print_user_input,
    print_info, print_status, print_warning, WARNING, MUTED
)
from logger import log

# ── Dictionary data ────────────────────────────────────────────────────────────
try:
    with open(DATA_FILE, "r", encoding="utf-8") as _f:
        _word_data: dict = json.load(_f)
    log.info(f"Dictionary loaded: {len(_word_data)} entries.")
except Exception as _e:
    _word_data = {}
    log.warning(f"Dictionary not loaded from {DATA_FILE}: {_e}")


# ── Notes helpers ──────────────────────────────────────────────────────────────

def _load_notes() -> list:
    """Load notes from JSON file in data/ directory."""
    if not NOTES_FILE.exists() and NOTES_FILE_LEGACY.exists():
        try:
            with open(NOTES_FILE_LEGACY, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            notes = []
            for line in lines:
                notes.append({
                    "id": len(notes) + 1,
                    "text": line,
                    "timestamp": "migrated",
                    "category": "general",
                })
            _save_notes(notes)
            log.info(f"Migrated {len(notes)} notes from data.txt → notes.json")
        except Exception as exc:
            log.warning(f"Notes migration failed: {exc}")
            return []

    if not NOTES_FILE.exists():
        return []
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        log.error(f"Failed to load notes: {exc}")
        return []


def _save_notes(notes: list) -> bool:
    """Persist notes list to data/notes.json."""
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        return True
    except Exception as exc:
        log.error(f"Failed to save notes: {exc}")
        return False


def save_note(note_text: str, category: str = "general") -> str:
    """Save a timestamped note."""
    notes = _load_notes()
    new_note = {
        "id": (notes[-1]["id"] + 1) if notes else 1,
        "text": note_text.strip(),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "category": category,
    }
    notes.append(new_note)
    if _save_notes(notes):
        log.info(f"Note saved: '{note_text[:60]}'")
        return f"Noted, Sir — I've saved: \"{note_text}\"."
    return "I was unable to save that note, Sir."


def read_notes() -> str:
    """Read the last 5 saved notes with timestamps."""
    notes = _load_notes()
    if not notes:
        return "You have no saved notes at this time, Sir."
    recent = notes[-5:]
    lines = [f"{n['timestamp']}  — {n['text']}" for n in recent]
    joined = " | ".join(lines)
    return f"Your most recent notes: {joined}."


def clear_notes() -> str:
    """Delete all saved notes."""
    if _save_notes([]):
        log.info("Notes cleared by user request.")
        return "All notes have been cleared, Sir."
    return "I was unable to clear the notes file, Sir."


# ── Dictionary ─────────────────────────────────────────────────────────────────

def translate(word: str) -> str:
    """Search for word definition in the built-in dictionary."""
    word = word.lower().strip()
    if not _word_data:
        return "The dictionary database is not loaded, Sir."
    if word in _word_data:
        res = _word_data[word]
        if isinstance(res, list):
            res = "; ".join(res)
        return f"Definition of '{word}': {res}"
    matches = get_close_matches(word, _word_data.keys(), n=1, cutoff=0.70)
    if matches:
        match = matches[0]
        res   = _word_data[match]
        if isinstance(res, list):
            res = "; ".join(res)
        return f"I could not find '{word}' exactly, but '{match}' means: {res}"
    return f"I could not find a definition for '{word}', Sir."


# ── Joke ───────────────────────────────────────────────────────────────────────

def joke() -> str:
    """Return a programmer-category joke."""
    try:
        return pyjokes.get_joke()
    except Exception:
        return "Why do programmers prefer dark mode? Because light attracts bugs!"


# ── Command Capture ────────────────────────────────────────────────────────────

def takeCommand(mode: str = "hybrid") -> str:
    """
    Capture user command via voice recognition and/or text input.
    """
    if mode == "text":
        try:
            cmd = input("\n  [Type Command] > ").strip()
            if cmd:
                print_user_input(cmd, "Text")
                log.info(f"Text command: '{cmd}'")
                return cmd
        except (KeyboardInterrupt, EOFError):
            raise
        return ""

    # Voice branch
    if sr is None:
        if mode == "hybrid":
            try:
                user_input = input("\n  [Type Command] > ").strip()
                if user_input:
                    print_user_input(user_input, "Text")
                    log.info(f"Hybrid text fallback: '{user_input}'")
                    return user_input
            except (KeyboardInterrupt, EOFError):
                raise
        return ""

    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.85
    r.energy_threshold = 300

    try:
        with sr.Microphone() as source:
            print_listening()
            r.adjust_for_ambient_noise(source, duration=0.4)
            audio = r.listen(source, timeout=4, phrase_time_limit=8)

        print_recognizing()
        query = r.recognize_google(audio, language="en-in")
        if query:
            print_user_input(query, "Voice")
            log.info(f"Voice command: '{query}'")
            return query

    except sr.WaitTimeoutError:
        log.debug("Voice timeout — no speech detected.")
    except sr.UnknownValueError:
        log.debug("Voice not understood.")
    except sr.RequestError as exc:
        log.warning(f"Speech API error: {exc}")
    except Exception as exc:
        log.warning(f"Microphone error: {exc}")

    # Hybrid text fallback
    if mode == "hybrid":
        try:
            user_input = input("\n  [Type Command] > ").strip()
            if user_input:
                print_user_input(user_input, "Text")
                log.info(f"Hybrid text fallback: '{user_input}'")
                return user_input
        except (KeyboardInterrupt, EOFError):
            raise

    return ""
