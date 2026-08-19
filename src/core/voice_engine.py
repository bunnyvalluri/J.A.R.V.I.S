"""
voice_engine.py — JARVIS Text-to-Speech Engine
================================================
Thread-safe singleton VoiceEngine wrapping pyttsx3.
Supports asynchronous background speech queueing, male/female voice
switching, rate/volume control, and graceful recovery.
"""

from __future__ import annotations

import sys
import queue
import threading
import pyttsx3
from pathlib import Path
from typing import Optional

# Ensure src in sys.path
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from logger import log
from config import CONFIG, save_config


class VoiceEngine:
    """Thread-safe singleton TTS engine with background queue support."""

    _instance: Optional["VoiceEngine"] = None

    def __new__(cls) -> "VoiceEngine":
        if cls._instance is None:
            cls._instance = super(VoiceEngine, cls).__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialised:
            return
        self._initialised = True
        self.engine = None
        self.voices = []
        self.enabled: bool = True
        self._queue: queue.Queue = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._init_engine()
        self._start_worker()

    def _init_engine(self) -> None:
        """Initialise or reinitialise the pyttsx3 engine."""
        try:
            self.engine = pyttsx3.init()
            self.voices = self.engine.getProperty("voices") or []
            self.set_rate(CONFIG.speech_rate)
            self.set_volume(CONFIG.speech_volume)

            gender = CONFIG.voice_gender
            if gender == "female" and len(self.voices) > 1:
                self.engine.setProperty("voice", self.voices[1].id)
            elif self.voices:
                self.engine.setProperty("voice", self.voices[0].id)

            self.enabled = CONFIG.voice_enabled
            log.info(
                f"VoiceEngine ready — gender={gender}, "
                f"rate={CONFIG.speech_rate}, voices={len(self.voices)}"
            )
        except Exception as exc:
            log.warning(f"VoiceEngine init failed: {exc}. Voice output disabled.")
            self.engine = None
            self.enabled = False

    def _start_worker(self) -> None:
        """Start the background speech worker thread."""
        def _worker():
            while True:
                item = self._queue.get()
                if item is None:
                    break
                text, done_event = item
                try:
                    with self._lock:
                        if self.enabled and self.engine and text:
                            self.engine.say(text)
                            self.engine.runAndWait()
                except Exception as exc:
                    log.warning(f"Voice worker speech error: {exc}")
                    try:
                        self._init_engine()
                    except Exception:
                        pass
                finally:
                    if done_event:
                        done_event.set()
                    self._queue.task_done()

        self._worker_thread = threading.Thread(target=_worker, daemon=True, name="JarvisTTSWorker")
        self._worker_thread.start()

    # ── Public API ─────────────────────────────────────────────────────────────

    def speak(self, text: str, block: bool = False) -> None:
        """Speak text aloud via non-blocking background queue."""
        if not self.enabled or not text or not text.strip():
            return

        done_event = threading.Event() if block else None
        self._queue.put((text.strip(), done_event))

        if block and done_event:
            done_event.wait(timeout=15.0)

    def switch_voice(self, gender: str = "male") -> str:
        """Switch between male and female voices."""
        with self._lock:
            if not self.engine or not self.voices:
                return "Voice switching is unavailable on this system."

            if gender.lower() == "female" and len(self.voices) > 1:
                self.engine.setProperty("voice", self.voices[1].id)
                CONFIG.voice_gender = "female"
                save_config(CONFIG)
                log.info("Voice switched to female.")
                return "Female voice profile activated, Sir."

            self.engine.setProperty("voice", self.voices[0].id)
            CONFIG.voice_gender = "male"
            save_config(CONFIG)
            log.info("Voice switched to male.")
            return "Male voice profile activated, Sir."

    def toggle_voice(self, enabled: Optional[bool] = None) -> str:
        """Enable or disable TTS output."""
        self.enabled = (not self.enabled) if enabled is None else enabled
        CONFIG.voice_enabled = self.enabled
        save_config(CONFIG)
        state = "enabled" if self.enabled else "muted"
        log.info(f"Voice output {state}.")
        return f"Voice output is now {state}, Sir."

    def set_rate(self, rate: int = 180) -> None:
        with self._lock:
            if self.engine:
                clamped = max(80, min(300, rate))
                self.engine.setProperty("rate", clamped)
                CONFIG.speech_rate = clamped
                save_config(CONFIG)

    def set_volume(self, volume: float = 1.0) -> None:
        with self._lock:
            if self.engine:
                clamped = max(0.0, min(1.0, volume))
                self.engine.setProperty("volume", clamped)
                CONFIG.speech_volume = clamped
                save_config(CONFIG)


# ── Module singleton ───────────────────────────────────────────────────────────
voice = VoiceEngine()


def speak(text: str, block: bool = False) -> None:
    """Module-level convenience wrapper."""
    voice.speak(text, block=block)
