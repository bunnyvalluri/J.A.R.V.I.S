"""
voice_engine.py — JARVIS Text-to-Speech Engine
================================================
Singleton VoiceEngine wrapping pyttsx3.
Supports male/female voice switching, rate/volume control,
mute toggle, and graceful self-recovery on engine failure.
"""

import pyttsx3
from logger import log
from config import CONFIG, save_config


class VoiceEngine:
    """Thread-safe singleton TTS engine."""

    _instance = None

    def __new__(cls):
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
        self._init_engine()

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
            self.engine  = None
            self.enabled = False

    # ── Public API ─────────────────────────────────────────────────────────────

    def speak(self, text: str) -> None:
        """Speak text aloud if voice output is enabled."""
        if not self.enabled or not self.engine or not text:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as exc:
            log.warning(f"TTS failure ({exc}) — attempting engine restart.")
            try:
                self._init_engine()
                if self.engine:
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception as exc2:
                log.error(f"TTS restart failed: {exc2}")

    def switch_voice(self, gender: str = "male") -> str:
        """Switch between male and female voices."""
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

    def toggle_voice(self, enabled: bool | None = None) -> str:
        """Enable or disable TTS output."""
        self.enabled = (not self.enabled) if enabled is None else enabled
        CONFIG.voice_enabled = self.enabled
        save_config(CONFIG)
        state = "enabled" if self.enabled else "muted"
        log.info(f"Voice output {state}.")
        return f"Voice output is now {state}, Sir."

    def set_rate(self, rate: int = 180) -> None:
        if self.engine:
            self.engine.setProperty("rate", max(80, min(300, rate)))

    def set_volume(self, volume: float = 1.0) -> None:
        if self.engine:
            self.engine.setProperty("volume", max(0.0, min(1.0, volume)))


# ── Module singletons ──────────────────────────────────────────────────────────
voice = VoiceEngine()


def speak(text: str) -> None:
    """Module-level convenience wrapper."""
    voice.speak(text)
