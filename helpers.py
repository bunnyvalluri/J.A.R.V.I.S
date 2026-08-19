import json
import pyjokes
import speech_recognition as sr
from difflib import get_close_matches
from pathlib import Path

from voice_engine import speak, voice
from weather_service import get_weather
from system_control import get_system_stats, take_screenshot, change_volume, lock_screen, get_time_and_date
from config import DATA_FILE, NOTES_FILE
from ui import print_listening, print_recognizing, print_user_input, print_jarvis_response, print_info, print_status, WARNING, MUTED

# Load dictionary data if available
try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    data = {}

def joke():
    """Tell a single humorous joke."""
    try:
        j = pyjokes.get_joke()
        return j
    except Exception:
        return "Why do programmers prefer dark mode? Because light attracts bugs!"

def cpu():
    """Report CPU and system stats."""
    spoken, display = get_system_stats()
    return spoken

def screenshot():
    """Capture a screenshot."""
    return take_screenshot()

def weather():
    """Fetch and report weather."""
    w = get_weather()
    return w.get("spoken", "Weather data is currently unavailable.")

def translate(word):
    """Search for word definition in dictionary."""
    word = word.lower().strip()
    if not data:
        return "Dictionary database is not loaded, Sir."

    if word in data:
        res = data[word]
        if isinstance(res, list):
            res = "; ".join(res)
        return f"Definition of {word}: {res}"
    
    matches = get_close_matches(word, data.keys(), n=1, cutoff=0.7)
    if matches:
        match = matches[0]
        res = data[match]
        if isinstance(res, list):
            res = "; ".join(res)
        return f"I couldn't find '{word}', but '{match}' means: {res}"
    
    return f"I couldn't find the definition for '{word}', Sir."

def save_note(note_text):
    """Save a note to memory."""
    try:
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(note_text + "\n")
        return f"I have noted that down: '{note_text}'."
    except Exception as e:
        return f"Failed to save note: {e}"

def read_notes():
    """Read all saved notes."""
    if not NOTES_FILE.exists():
        return "You have not saved any notes yet, Sir."
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        if not lines:
            return "Your notes list is currently empty, Sir."
        notes_str = "; ".join(lines[-5:])  # read up to last 5 notes
        return f"Here are your latest saved notes: {notes_str}."
    except Exception as e:
        return f"Failed to read notes: {e}"

def clear_notes():
    """Clear all saved notes."""
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            f.write("")
        return "All notes have been cleared, Sir."
    except Exception as e:
        return f"Failed to clear notes: {e}"

def takeCommand(mode="hybrid"):
    """
    Intelligent command capture supporting Voice and Text.
    mode can be 'hybrid', 'voice', or 'text'.
    """
    if mode == "text":
        try:
            cmd = input("\n[Type Command]: ").strip()
            if cmd:
                print_user_input(cmd, "Text")
                return cmd
        except (KeyboardInterrupt, EOFError):
            raise
        return ""

    # Try voice recognition
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            print_listening()
            r.adjust_for_ambient_noise(source, duration=0.6)
            audio = r.listen(source, timeout=3.5, phrase_time_limit=7)
        
        print_recognizing()
        query = r.recognize_google(audio, language='en-in')
        if query:
            print_user_input(query, "Voice")
            return query
    except sr.WaitTimeoutError:
        pass
    except sr.UnknownValueError:
        pass
    except Exception as e:
        # If mic fails or is unavailable, fallback gracefully
        pass

    # In hybrid mode, provide text fallback prompt if mic heard nothing
    if mode == "hybrid":
        try:
            user_input = input("\n[Type Command or Press Enter]: ").strip()
            if user_input:
                print_user_input(user_input, "Text")
                return user_input
        except (KeyboardInterrupt, EOFError):
            raise

    return ""
