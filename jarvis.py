import os
import sys
import datetime
import argparse
import wikipedia

from config import CONFIG, save_config
from ui import (
    print_banner, print_diagnostics, print_jarvis_response,
    print_info, print_warning, print_error, print_help, print_status,
    PRIMARY, SUCCESS, WARNING, HIGHLIGHT
)
from voice_engine import speak, voice
from helpers import (
    takeCommand, weather, cpu, screenshot, joke,
    translate, save_note, read_notes, clear_notes
)
from weather_service import get_weather
from news import speak_news, getNewsUrl
from app_launcher import (
    open_whatsapp, open_vscode, open_spotify, open_calculator,
    open_notepad, open_terminal, open_file_explorer, open_task_manager,
    search_youtube, search_google, open_url, open_custom_website_or_app
)
from system_control import (
    get_system_stats, take_screenshot, change_volume,
    lock_screen, get_time_and_date, get_network_info
)

class JarvisAssistant:
    def __init__(self, mode="hybrid"):
        self.user_name = CONFIG.get("user_name", "Sir")
        self.assistant_name = CONFIG.get("assistant_name", "JARVIS")
        self.mode = mode

    def respond(self, message):
        """Display and optionally speak assistant response."""
        print_jarvis_response(message)
        speak(message)

    def wish_me(self):
        """Initial startup greeting based on time of day."""
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            greeting = f"Good morning, {self.user_name}."
        elif 12 <= hour < 18:
            greeting = f"Good afternoon, {self.user_name}."
        else:
            greeting = f"Good evening, {self.user_name}."

        welcome_msg = f"{greeting} I am {self.assistant_name}. All systems are fully operational and ready for your commands."
        self.respond(welcome_msg)

    def execute_command(self, query):
        """Main natural language intent processing engine."""
        if not query or query.strip() == "none":
            return True

        query_lower = query.lower().strip()

        # ------------------ 1. EXIT & TERMINATION ------------------
        if any(w == query_lower for w in ["exit", "quit", "stop", "sleep", "goodbye", "bye", "shutdown"]):
            farewell = f"Goodbye, {self.user_name}. Systems powering down."
            self.respond(farewell)
            return False

        # ------------------ 2. GREETINGS & CHIT-CHAT ------------------
        elif query_lower in ["hi", "hello", "hey", "hola", "namaste"]:
            self.respond(f"Hello {self.user_name}! How may I assist you today?")

        elif "how are you" in query_lower:
            self.respond(f"I am functioning at peak efficiency, {self.user_name}. Thank you for asking!")

        elif "who are you" in query_lower or "your name" in query_lower:
            self.respond(f"I am {self.assistant_name}, your personal Just A Rather Very Intelligent System.")

        elif "who made you" in query_lower or "who created you" in query_lower:
            self.respond("I was engineered as an advanced personal AI desktop assistant.")

        elif "jarvis are you there" in query_lower or "are you online" in query_lower:
            self.respond(f"Always at your service, {self.user_name}.")

        elif "thank you" in query_lower or "thanks" in query_lower:
            self.respond(f"You are most welcome, {self.user_name}.")

        elif query_lower in ["help", "what can you do", "commands", "show commands"]:
            print_help()
            self.respond("I have displayed the list of available command capabilities on your screen.")

        # ------------------ 3. APP LAUNCHER & WEB ------------------
        elif "whatsapp" in query_lower:
            msg = open_whatsapp()
            self.respond(msg)

        elif "vscode" in query_lower or "vs code" in query_lower or query_lower == "open code":
            msg = open_vscode()
            self.respond(msg)

        elif "spotify" in query_lower:
            msg = open_spotify()
            self.respond(msg)

        elif "calculator" in query_lower or query_lower == "calc":
            msg = open_calculator()
            self.respond(msg)

        elif "notepad" in query_lower:
            msg = open_notepad()
            self.respond(msg)

        elif "terminal" in query_lower or "powershell" in query_lower or "command prompt" in query_lower:
            msg = open_terminal()
            self.respond(msg)

        elif "task manager" in query_lower:
            msg = open_task_manager()
            self.respond(msg)

        elif "file explorer" in query_lower or query_lower == "open files":
            msg = open_file_explorer()
            self.respond(msg)

        elif "open youtube" in query_lower:
            open_url("https://youtube.com")
            self.respond("Opening YouTube, Sir.")

        elif "open google" in query_lower:
            open_url("https://google.com")
            self.respond("Opening Google, Sir.")

        elif "open github" in query_lower:
            open_url("https://github.com")
            self.respond("Opening GitHub, Sir.")

        elif "open chatgpt" in query_lower or "open chat gpt" in query_lower:
            open_url("https://chatgpt.com")
            self.respond("Opening ChatGPT, Sir.")

        elif "open stackoverflow" in query_lower:
            open_url("https://stackoverflow.com")
            self.respond("Opening Stack Overflow, Sir.")

        elif "open amazon" in query_lower:
            open_url("https://amazon.com")
            self.respond("Opening Amazon, Sir.")

        # ------------------ 4. SEARCHES & MEDIA ------------------
        elif "play" in query_lower and "on youtube" in query_lower:
            search_term = query_lower.replace("play", "").replace("on youtube", "").strip()
            msg = search_youtube(search_term)
            self.respond(msg)

        elif query_lower.startswith("search youtube for "):
            search_term = query_lower.replace("search youtube for ", "").strip()
            msg = search_youtube(search_term)
            self.respond(msg)

        elif query_lower.startswith("search google for ") or query_lower.startswith("search for "):
            search_term = query_lower.replace("search google for ", "").replace("search for ", "").strip()
            msg = search_google(search_term)
            self.respond(msg)

        elif query_lower.startswith("google "):
            search_term = query_lower.replace("google ", "").strip()
            msg = search_google(search_term)
            self.respond(msg)

        elif "wikipedia" in query_lower or query_lower.startswith("who is ") or query_lower.startswith("what is "):
            topic = query_lower.replace("wikipedia", "").replace("search", "").replace("who is", "").replace("what is", "").strip()
            if topic:
                try:
                    self.respond(f"Searching Wikipedia for {topic}...")
                    summary = wikipedia.summary(topic, sentences=2)
                    self.respond(f"According to Wikipedia: {summary}")
                except Exception:
                    # Fallback to google search
                    msg = search_google(topic)
                    self.respond(f"I could not locate a direct Wikipedia summary, so I've searched Google for '{topic}'.")
            else:
                self.respond("Please specify the topic you would like me to search.")

        # ------------------ 5. LIVE WEATHER & NEWS ------------------
        elif any(k in query_lower for k in ["weather", "temperature", "forecast", "climate"]):
            w = get_weather()
            print_status("WEATHER", w.get("display", ""), HIGHLIGHT)
            self.respond(w.get("spoken", "Weather data is currently unavailable."))

        elif any(k in query_lower for k in ["news", "headlines", "top stories"]):
            speak_news(speaker_func=self.respond, limit=4)

        # ------------------ 6. SYSTEM CONTROLS & TELEMETRY ------------------
        elif any(k in query_lower for k in ["cpu", "system stats", "battery", "ram", "memory usage", "hardware"]):
            spoken, display = get_system_stats()
            print_status("SYSTEM", f"CPU: {display['cpu']} | RAM: {display['ram']} | Disk: {display['disk']} | Battery: {display['battery']}", PRIMARY)
            self.respond(spoken)

        elif "screenshot" in query_lower:
            msg = take_screenshot()
            self.respond(msg)

        elif "volume up" in query_lower or "increase volume" in query_lower:
            msg = change_volume("up")
            self.respond(msg)

        elif "volume down" in query_lower or "decrease volume" in query_lower:
            msg = change_volume("down")
            self.respond(msg)

        elif "mute" in query_lower or "unmute" in query_lower:
            msg = change_volume("mute")
            self.respond(msg)

        elif "lock screen" in query_lower or "lock workstation" in query_lower or query_lower == "lock pc":
            msg = lock_screen()
            self.respond(msg)

        elif any(k in query_lower for k in ["time", "the time", "current time", "date", "today's date"]):
            msg = get_time_and_date()
            self.respond(msg)

        elif "ip address" in query_lower or "network info" in query_lower or query_lower == "my ip":
            msg = get_network_info()
            self.respond(msg)

        # ------------------ 7. MEMORY & NOTES ------------------
        elif query_lower.startswith("remember that ") or query_lower.startswith("note down "):
            note = query_lower.replace("remember that ", "").replace("note down ", "").strip()
            msg = save_note(note)
            self.respond(msg)

        elif "what did i ask you to remember" in query_lower or "read notes" in query_lower or "show notes" in query_lower:
            msg = read_notes()
            self.respond(msg)

        elif "clear notes" in query_lower or "delete notes" in query_lower or "forget notes" in query_lower:
            msg = clear_notes()
            self.respond(msg)

        # ------------------ 8. DICTIONARY & JOKES ------------------
        elif query_lower.startswith("define ") or query_lower.startswith("meaning of ") or "dictionary" in query_lower:
            word = query_lower.replace("define", "").replace("meaning of", "").replace("dictionary", "").strip()
            if word:
                res = translate(word)
                self.respond(res)
            else:
                self.respond("Please tell me which word you would like me to define.")

        elif "joke" in query_lower:
            j = joke()
            self.respond(j)

        # ------------------ 9. VOICE & MODE SETTINGS ------------------
        elif "female voice" in query_lower:
            msg = voice.switch_voice("female")
            self.respond(msg)

        elif "male voice" in query_lower:
            msg = voice.switch_voice("male")
            self.respond(msg)

        elif "mute voice" in query_lower or "disable voice" in query_lower:
            msg = voice.toggle_voice(False)
            self.respond(msg)

        elif "enable voice" in query_lower or "unmute voice" in query_lower:
            msg = voice.toggle_voice(True)
            self.respond(msg)

        elif "switch to text" in query_lower or "text mode" in query_lower:
            self.mode = "text"
            self.respond("Switched to Text Mode. Voice recognition is paused.")

        elif "switch to voice" in query_lower or "voice mode" in query_lower:
            self.mode = "voice"
            self.respond("Switched to Voice Mode. Microphones active.")

        elif "switch to hybrid" in query_lower or "hybrid mode" in query_lower:
            self.mode = "hybrid"
            self.respond("Switched to Hybrid Mode.")

        # ------------------ 10. GENERIC FALLBACK ------------------
        elif query_lower.startswith("open "):
            target = query_lower.replace("open ", "").strip()
            msg = open_custom_website_or_app(target)
            self.respond(msg)

        else:
            # Smart search fallback
            msg = search_google(query)
            self.respond(f"I wasn't sure how to handle '{query}' locally, so I looked it up on Google for you.")

        return True

    def run(self):
        """Start the JARVIS assistant interaction loop."""
        print_banner(version="2.0 Pro", user=self.user_name)
        print_diagnostics()
        self.wish_me()

        print_info(f"Interaction Mode: [{self.mode.upper()}] | Type 'help' for commands, 'exit' to quit.")

        while True:
            try:
                query = takeCommand(mode=self.mode)
                if query:
                    should_continue = self.execute_command(query)
                    if not should_continue:
                        break
            except KeyboardInterrupt:
                print("\n")
                self.respond("Shutdown signal received. Goodbye Sir.")
                break
            except Exception as e:
                print_error(f"Unexpected error: {e}")

def main():
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Personal AI Assistant")
    parser.add_argument("-t", "--text", action="store_true", help="Start in Text-only mode")
    parser.add_argument("-v", "--voice", action="store_true", help="Start in Voice-only mode")
    parser.add_argument("--test", type=str, help="Execute a single test command and exit")
    args = parser.parse_args()

    mode = "hybrid"
    if args.text:
        mode = "text"
    elif args.voice:
        mode = "voice"

    assistant = JarvisAssistant(mode=mode)

    if args.test:
        print_status("TEST", f"Executing test command: '{args.test}'", HIGHLIGHT)
        assistant.execute_command(args.test)
        return

    assistant.run()

if __name__ == "__main__":
    main()
