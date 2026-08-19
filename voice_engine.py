import pyttsx3
from config import CONFIG, save_config

class VoiceEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoiceEngine, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.voices = self.engine.getProperty('voices')
            self.set_rate(CONFIG.get("speech_rate", 180))
            self.set_volume(CONFIG.get("speech_volume", 1.0))
            
            # Select gender
            gender = CONFIG.get("voice_gender", "male")
            if gender == "female" and len(self.voices) > 1:
                self.engine.setProperty('voice', self.voices[1].id)
            elif len(self.voices) > 0:
                self.engine.setProperty('voice', self.voices[0].id)
                
            self.enabled = CONFIG.get("voice_enabled", True)
        except Exception as e:
            print(f"[VoiceEngine Init Warning: {e}]")
            self.engine = None
            self.enabled = False

    def speak(self, text):
        """Speak the provided text aloud if voice output is enabled."""
        if not self.enabled or not self.engine or not text:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            # Reinitialize engine on failure
            try:
                self._init_engine()
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass

    def switch_voice(self, gender="male"):
        """Switch between male and female voices."""
        if not self.engine or not self.voices:
            return "Voice switching is not available on this system."
        
        if gender.lower() == "female" and len(self.voices) > 1:
            self.engine.setProperty('voice', self.voices[1].id)
            CONFIG["voice_gender"] = "female"
            save_config(CONFIG)
            return "Voice switched to female voice, Sir."
        elif len(self.voices) > 0:
            self.engine.setProperty('voice', self.voices[0].id)
            CONFIG["voice_gender"] = "male"
            save_config(CONFIG)
            return "Voice switched to male voice, Sir."
        return "Only one voice profile is available."

    def toggle_voice(self, enabled=None):
        """Toggle or set voice output state."""
        if enabled is None:
            self.enabled = not self.enabled
        else:
            self.enabled = enabled
        CONFIG["voice_enabled"] = self.enabled
        save_config(CONFIG)
        state = "enabled" if self.enabled else "muted"
        return f"Voice output is now {state}, Sir."

    def set_rate(self, rate=180):
        if self.engine:
            self.engine.setProperty('rate', rate)

    def set_volume(self, volume=1.0):
        if self.engine:
            self.engine.setProperty('volume', volume)

# Singleton instance
voice = VoiceEngine()

def speak(text):
    voice.speak(text)
