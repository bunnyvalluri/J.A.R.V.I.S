"""
jarvis.py — JARVIS Core Controller
=====================================
Lead Engineer: Production-Grade AI Assistant
Version: 2.0 Pro

Architecture:
  - CommandRegistry: maps keyword/regex patterns → handler methods
  - GeminiBrain: Gemini 2.0 Flash as intelligent fallback
  - Session tracking: ID, start time, command count, history
  - Structured logging throughout
  - CLI flags: --text, --voice, --friday, --test
"""

import os
import sys
import datetime
import argparse
import wikipedia

from config import CONFIG, save_config
from logger import log, get_session_id
from ui import (
    print_banner, print_diagnostics, print_jarvis_response,
    print_llm_response, print_thinking,
    print_info, print_warning, print_error, print_help,
    print_status, print_session_end,
    print_selftest_header, print_selftest_footer, print_module_status,
    PRIMARY, SUCCESS, WARNING, HIGHLIGHT, LLM_CLR
)
from voice_engine import speak, voice
from helpers import (
    takeCommand, joke, translate, save_note, read_notes, clear_notes
)
from weather_service import get_weather
from news import speak_news
from app_launcher import (
    open_whatsapp, open_vscode, open_spotify, open_calculator,
    open_notepad, open_terminal, open_file_explorer, open_task_manager,
    search_youtube, search_google, open_url, open_custom_website_or_app
)
from system_control import (
    get_system_stats, take_screenshot, change_volume,
    lock_screen, get_time_and_date, get_network_info
)
from ai_brain import GeminiBrain


# ══════════════════════════════════════════════════════════════════════════════
# Self-Test
# ══════════════════════════════════════════════════════════════════════════════

def run_selftest(brain: GeminiBrain) -> dict:
    """
    Run a quick startup health check on all subsystems.
    Returns a dict of module → bool (pass/fail).
    """
    results = {}

    # Voice engine
    try:
        from voice_engine import voice as _v
        results["Voice Engine"] = (_v.engine is not None)
    except Exception:
        results["Voice Engine"] = False

    # Microphone
    try:
        import speech_recognition as sr
        sr.Microphone()
        results["Microphone"] = True
    except Exception:
        results["Microphone"] = False

    # Weather service (import only — don't hit API at startup)
    try:
        from weather_service import get_weather as _w
        results["Weather Service"] = True
    except Exception:
        results["Weather Service"] = False

    # News module
    try:
        from news import fetch_headlines as _n
        results["News Feed"] = True
    except Exception:
        results["News Feed"] = False

    # Dictionary
    try:
        from helpers import _word_data
        results["Dictionary"] = bool(_word_data)
    except Exception:
        results["Dictionary"] = False

    # Gemini AI
    results["Gemini AI Brain"] = brain.available

    # Logs directory
    try:
        from config import LOG_DIR
        results["Log System"] = LOG_DIR.exists()
    except Exception:
        results["Log System"] = False

    return results


# ══════════════════════════════════════════════════════════════════════════════
# Command Registry
# ══════════════════════════════════════════════════════════════════════════════

class CommandRegistry:
    """
    Priority-ordered intent dispatcher.
    Each entry is a (matcher_fn, handler_fn) tuple.
    The first matcher that returns True wins.
    """

    def __init__(self, assistant: "JarvisAssistant") -> None:
        self.a = assistant
        self._routes: list = []
        self._register_all()

    def _register_all(self) -> None:
        a = self.a

        def r(matcher, handler):
            self._routes.append((matcher, handler))

        # ── Exit ──────────────────────────────────────────────────────────────
        r(lambda q: q in {"exit", "quit", "stop", "sleep", "goodbye", "bye", "shutdown"},
          a._cmd_exit)

        # ── Help ──────────────────────────────────────────────────────────────
        r(lambda q: q in {"help", "what can you do", "commands", "show commands"},
          a._cmd_help)

        # ── Greetings ─────────────────────────────────────────────────────────
        r(lambda q: q in {"hi", "hello", "hey", "hola", "namaste"},
          a._cmd_greet)

        r(lambda q: "how are you" in q,              a._cmd_status)
        r(lambda q: "who are you" in q or "your name" in q, a._cmd_identity)
        r(lambda q: "who made you" in q or "who created you" in q, a._cmd_creator)
        r(lambda q: "are you there" in q or "are you online" in q, a._cmd_ping)
        r(lambda q: "thank you" in q or q == "thanks", a._cmd_thanks)

        # ── App Launcher ──────────────────────────────────────────────────────
        r(lambda q: "whatsapp" in q,  a._cmd_whatsapp)
        r(lambda q: "vscode" in q or "vs code" in q or q == "open code", a._cmd_vscode)
        r(lambda q: "spotify" in q,   a._cmd_spotify)
        r(lambda q: "calculator" in q or q == "calc", a._cmd_calculator)
        r(lambda q: "notepad" in q,   a._cmd_notepad)
        r(lambda q: "terminal" in q or "powershell" in q or "command prompt" in q, a._cmd_terminal)
        r(lambda q: "task manager" in q, a._cmd_task_manager)
        r(lambda q: "file explorer" in q or q == "open files", a._cmd_explorer)

        # ── Web shortcuts ─────────────────────────────────────────────────────
        r(lambda q: q == "open youtube",     a._cmd_open_youtube)
        r(lambda q: q == "open google",      a._cmd_open_google)
        r(lambda q: q == "open github",      a._cmd_open_github)
        r(lambda q: "open chatgpt" in q,     a._cmd_open_chatgpt)
        r(lambda q: "open stackoverflow" in q, a._cmd_open_so)
        r(lambda q: q == "open amazon",      a._cmd_open_amazon)

        # ── Search & Media ─────────────────────────────────────────────────────
        r(lambda q: "play" in q and "youtube" in q,   a._cmd_play_youtube)
        r(lambda q: q.startswith("search youtube for "), a._cmd_search_youtube)
        r(lambda q: q.startswith("search google for ") or q.startswith("search for "), a._cmd_search_google)
        r(lambda q: q.startswith("google "),           a._cmd_google)

        # ── System Controls ───────────────────────────────────────────────────
        r(lambda q: any(k in q for k in ("cpu", "system stats", "battery", "ram", "memory usage", "hardware")), a._cmd_sysinfo)
        r(lambda q: "screenshot" in q,         a._cmd_screenshot)
        r(lambda q: "volume up" in q or "increase volume" in q, a._cmd_vol_up)
        r(lambda q: "volume down" in q or "decrease volume" in q, a._cmd_vol_down)
        r(lambda q: "mute" in q or "unmute" in q, a._cmd_mute)
        r(lambda q: "lock screen" in q or "lock workstation" in q or q == "lock pc", a._cmd_lock)
        r(lambda q: any(k in q for k in ("time", "current time", "date", "today")), a._cmd_time)
        r(lambda q: "ip address" in q or "network info" in q or q == "my ip", a._cmd_network)

        # ── Weather & News ────────────────────────────────────────────────────
        r(lambda q: any(k in q for k in ("weather", "temperature", "forecast", "climate")), a._cmd_weather)
        r(lambda q: any(k in q for k in ("news", "headlines", "top stories")), a._cmd_news)

        # ── Wikipedia (after system routes so "what is the time" doesn’t land here) ─
        r(lambda q: "wikipedia" in q or q.startswith("who is ") or q.startswith("what is "), a._cmd_wikipedia)

        # ── Notes & Memory ────────────────────────────────────────────────────
        r(lambda q: q.startswith("remember that ") or q.startswith("note down "), a._cmd_save_note)
        r(lambda q: "what did i ask" in q or "read notes" in q or "show notes" in q, a._cmd_read_notes)
        r(lambda q: "clear notes" in q or "delete notes" in q or "forget notes" in q, a._cmd_clear_notes)

        # ── Dictionary & Jokes ────────────────────────────────────────────────
        r(lambda q: q.startswith("define ") or q.startswith("meaning of ") or "dictionary" in q, a._cmd_define)
        r(lambda q: "joke" in q, a._cmd_joke)

        # ── Voice Settings ────────────────────────────────────────────────────
        r(lambda q: "female voice" in q, a._cmd_voice_female)
        r(lambda q: "male voice" in q,   a._cmd_voice_male)
        r(lambda q: "mute voice" in q or "disable voice" in q, a._cmd_voice_mute)
        r(lambda q: "enable voice" in q or "unmute voice" in q, a._cmd_voice_enable)
        r(lambda q: "switch to friday" in q or "friday mode" in q, a._cmd_persona_friday)
        r(lambda q: "switch to jarvis" in q or "jarvis mode" in q, a._cmd_persona_jarvis)

        # ── Mode Switching ────────────────────────────────────────────────────
        r(lambda q: "text mode" in q or "switch to text" in q, a._cmd_mode_text)
        r(lambda q: "voice mode" in q or "switch to voice" in q, a._cmd_mode_voice)
        r(lambda q: "hybrid mode" in q or "switch to hybrid" in q, a._cmd_mode_hybrid)

        # ── AI Brain direct invoke ────────────────────────────────────────────
        r(lambda q: q.startswith("ask jarvis ") or q.startswith("ask ai "), a._cmd_ask_ai)

        # ── Generic "open X" ──────────────────────────────────────────────────
        r(lambda q: q.startswith("open "), a._cmd_open_generic)

    def dispatch(self, query: str) -> bool:
        """
        Find the first matching route and call its handler.
        Returns False if JARVIS should shut down, True to continue.
        """
        q = query.lower().strip()
        for matcher, handler in self._routes:
            try:
                if matcher(q):
                    log.info(f"Command matched → {handler.__name__}  query='{query[:60]}'")
                    return handler(query, q)
            except Exception as exc:
                log.error(f"Route matcher error: {exc}")
                continue

        # ── Gemini AI fallback ─────────────────────────────────────────────────
        log.info(f"No local match — delegating to GeminiBrain: '{query[:60]}'")
        return self.a._cmd_ai_fallback(query, q)


# ══════════════════════════════════════════════════════════════════════════════
# JarvisAssistant
# ══════════════════════════════════════════════════════════════════════════════

class JarvisAssistant:
    """
    Core JARVIS assistant controller.
    Owns the session lifecycle, command dispatch, TTS, and logging.
    """

    VERSION = "2.0 Pro"

    def __init__(self, mode: str = "hybrid") -> None:
        self.user_name      = CONFIG.user_name
        self.assistant_name = CONFIG.assistant_name
        self.mode           = mode
        self.session_id     = get_session_id()
        self.start_time     = datetime.datetime.now()
        self.command_count  = 0
        self.history: list  = []

        log.info(f"Session {self.session_id} started — mode={mode}, user={self.user_name}")

        # Initialise Gemini brain
        self.brain = GeminiBrain(user_name=self.user_name)

        # Build command registry
        self.registry = CommandRegistry(self)

    # ── Core I/O ──────────────────────────────────────────────────────────────

    def respond(self, message: str, is_llm: bool = False) -> None:
        """Display and speak an assistant response."""
        if is_llm:
            print_llm_response(message)
        else:
            print_jarvis_response(message)
        speak(message)
        self.history.append({"role": "assistant", "text": message,
                              "ts": datetime.datetime.now().isoformat()})

    def execute_command(self, query: str) -> bool:
        """Entry point: validate, log, and dispatch a command."""
        if not query or query.strip().lower() == "none":
            return True
        self.command_count += 1
        self.history.append({"role": "user", "text": query,
                              "ts": datetime.datetime.now().isoformat()})
        try:
            return self.registry.dispatch(query)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            log.error(f"Unhandled error in execute_command: {exc}", exc_info=True)
            print_error(f"An unexpected error occurred: {exc}")
            return True

    # ── Startup ───────────────────────────────────────────────────────────────

    def wish_me(self) -> None:
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            greeting = f"Good morning, {self.user_name}."
        elif 12 <= hour < 18:
            greeting = f"Good afternoon, {self.user_name}."
        else:
            greeting = f"Good evening, {self.user_name}."
        self.respond(
            f"{greeting} I am {self.assistant_name}, version {self.VERSION}. "
            f"All systems are fully operational and standing by for your commands."
        )

    def run(self) -> None:
        """Main interaction loop."""
        print_banner(version=self.VERSION, user=self.user_name, session_id=self.session_id)
        print_diagnostics()

        # Self-test
        test_results = run_selftest(self.brain)
        print_selftest_header()
        for module, ok in test_results.items():
            detail = "Gemini API key found" if (module == "Gemini AI Brain" and ok) else (
                     "No API key — set GEMINI_API_KEY in .env" if (module == "Gemini AI Brain" and not ok) else "")
            print_module_status(module, ok, detail)
        print_selftest_footer()

        self.wish_me()
        print_info(
            f"Mode: [{self.mode.upper()}]  |  "
            f"AI Brain: {'ONLINE' if self.brain.available else 'OFFLINE'}  |  "
            f"Type 'help' for commands, 'exit' to quit."
        )
        print()

        while True:
            try:
                query = takeCommand(mode=self.mode)
                if query:
                    should_continue = self.execute_command(query)
                    if not should_continue:
                        break
            except KeyboardInterrupt:
                print("\n")
                self.respond(f"Keyboard interrupt detected. Shutting down, {self.user_name}.")
                break
            except Exception as exc:
                log.error(f"Main loop error: {exc}", exc_info=True)
                print_error(f"Unexpected error: {exc}")

        print_session_end(self.command_count, self.start_time)
        log.info(
            f"Session {self.session_id} ended — "
            f"commands={self.command_count}, "
            f"duration={(datetime.datetime.now() - self.start_time).seconds}s"
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Command Handlers
    # Each handler receives (raw_query, query_lower) and returns bool.
    # ══════════════════════════════════════════════════════════════════════════

    # ── Exit ──────────────────────────────────────────────────────────────────
    def _cmd_exit(self, q, ql) -> bool:
        elapsed = datetime.datetime.now() - self.start_time
        mins    = int(elapsed.total_seconds() // 60)
        self.respond(
            f"Goodbye, {self.user_name}. Session duration: {mins} minute{'s' if mins != 1 else ''}. "
            f"All systems powering down."
        )
        return False

    # ── Help ──────────────────────────────────────────────────────────────────
    def _cmd_help(self, q, ql) -> bool:
        print_help()
        self.respond("I've displayed my full capability list on your screen, Sir.")
        return True

    # ── Greetings ─────────────────────────────────────────────────────────────
    def _cmd_greet(self, q, ql) -> bool:
        self.respond(f"Hello, {self.user_name}. How may I assist you?")
        return True

    def _cmd_status(self, q, ql) -> bool:
        self.respond(f"All systems are functioning at peak efficiency, {self.user_name}. Thank you for asking.")
        return True

    def _cmd_identity(self, q, ql) -> bool:
        self.respond(f"I am {self.assistant_name} — Just A Rather Very Intelligent System, version {self.VERSION}.")
        return True

    def _cmd_creator(self, q, ql) -> bool:
        self.respond("I was engineered as an advanced personal AI desktop assistant. My architecture was designed for production-grade reliability.")
        return True

    def _cmd_ping(self, q, ql) -> bool:
        self.respond(f"Always present and fully operational, {self.user_name}.")
        return True

    def _cmd_thanks(self, q, ql) -> bool:
        self.respond(f"You are most welcome, {self.user_name}. Is there anything else I can do for you?")
        return True

    # ── App Launcher ──────────────────────────────────────────────────────────
    def _cmd_whatsapp(self, q, ql) -> bool:
        self.respond(open_whatsapp()); return True

    def _cmd_vscode(self, q, ql) -> bool:
        self.respond(open_vscode()); return True

    def _cmd_spotify(self, q, ql) -> bool:
        self.respond(open_spotify()); return True

    def _cmd_calculator(self, q, ql) -> bool:
        self.respond(open_calculator()); return True

    def _cmd_notepad(self, q, ql) -> bool:
        self.respond(open_notepad()); return True

    def _cmd_terminal(self, q, ql) -> bool:
        self.respond(open_terminal()); return True

    def _cmd_task_manager(self, q, ql) -> bool:
        self.respond(open_task_manager()); return True

    def _cmd_explorer(self, q, ql) -> bool:
        self.respond(open_file_explorer()); return True

    # ── Web Shortcuts ─────────────────────────────────────────────────────────
    def _open_site(self, url: str, name: str) -> bool:
        open_url(url); self.respond(f"Opening {name}, Sir."); return True

    def _cmd_open_youtube(self, q, ql) -> bool:
        return self._open_site("https://youtube.com", "YouTube")

    def _cmd_open_google(self, q, ql) -> bool:
        return self._open_site("https://google.com", "Google")

    def _cmd_open_github(self, q, ql) -> bool:
        return self._open_site("https://github.com", "GitHub")

    def _cmd_open_chatgpt(self, q, ql) -> bool:
        return self._open_site("https://chatgpt.com", "ChatGPT")

    def _cmd_open_so(self, q, ql) -> bool:
        return self._open_site("https://stackoverflow.com", "Stack Overflow")

    def _cmd_open_amazon(self, q, ql) -> bool:
        return self._open_site("https://amazon.com", "Amazon")

    # ── Search & Media ────────────────────────────────────────────────────────
    def _cmd_play_youtube(self, q, ql) -> bool:
        term = ql.replace("play", "").replace("on youtube", "").strip()
        self.respond(search_youtube(term)); return True

    def _cmd_search_youtube(self, q, ql) -> bool:
        term = ql.replace("search youtube for", "").strip()
        self.respond(search_youtube(term)); return True

    def _cmd_search_google(self, q, ql) -> bool:
        term = ql.replace("search google for", "").replace("search for", "").strip()
        self.respond(search_google(term)); return True

    def _cmd_google(self, q, ql) -> bool:
        term = ql.replace("google", "", 1).strip()
        self.respond(search_google(term)); return True

    def _cmd_wikipedia(self, q, ql) -> bool:
        topic = (ql.replace("wikipedia", "").replace("search", "")
                   .replace("who is", "").replace("what is", "").strip())
        if not topic:
            self.respond("Please specify the topic you would like me to look up.")
            return True
        try:
            self.respond(f"Searching Wikipedia for {topic}, one moment...")
            summary = wikipedia.summary(topic, sentences=2)
            self.respond(f"According to Wikipedia: {summary}")
        except Exception:
            self.respond(search_google(topic))
            self.respond(f"Wikipedia had no direct summary for '{topic}', so I've searched Google instead.")
        return True

    # ── Weather & News ────────────────────────────────────────────────────────
    def _cmd_weather(self, q, ql) -> bool:
        w = get_weather()
        print_status("WEATHER", w.get("display", ""), HIGHLIGHT)
        self.respond(w.get("spoken", "Weather data is currently unavailable."))
        return True

    def _cmd_news(self, q, ql) -> bool:
        speak_news(speaker_func=self.respond, limit=CONFIG.max_news_headlines)
        return True

    # ── System Controls ───────────────────────────────────────────────────────
    def _cmd_sysinfo(self, q, ql) -> bool:
        spoken, display = get_system_stats()
        print_status("SYSTEM",
            f"CPU: {display['cpu']} | RAM: {display['ram']} | "
            f"Disk: {display['disk']} | Power: {display['battery']}", PRIMARY)
        self.respond(spoken); return True

    def _cmd_screenshot(self, q, ql) -> bool:
        self.respond(take_screenshot()); return True

    def _cmd_vol_up(self, q, ql) -> bool:
        self.respond(change_volume("up")); return True

    def _cmd_vol_down(self, q, ql) -> bool:
        self.respond(change_volume("down")); return True

    def _cmd_mute(self, q, ql) -> bool:
        self.respond(change_volume("mute")); return True

    def _cmd_lock(self, q, ql) -> bool:
        self.respond(lock_screen()); return True

    def _cmd_time(self, q, ql) -> bool:
        self.respond(get_time_and_date()); return True

    def _cmd_network(self, q, ql) -> bool:
        self.respond(get_network_info()); return True

    # ── Notes & Memory ────────────────────────────────────────────────────────
    def _cmd_save_note(self, q, ql) -> bool:
        note = ql.replace("remember that", "").replace("note down", "").strip()
        self.respond(save_note(note)); return True

    def _cmd_read_notes(self, q, ql) -> bool:
        self.respond(read_notes()); return True

    def _cmd_clear_notes(self, q, ql) -> bool:
        self.respond(clear_notes()); return True

    # ── Dictionary & Jokes ────────────────────────────────────────────────────
    def _cmd_define(self, q, ql) -> bool:
        word = ql.replace("define", "").replace("meaning of", "").replace("dictionary", "").strip()
        self.respond(translate(word) if word else "Please specify the word you would like defined.")
        return True

    def _cmd_joke(self, q, ql) -> bool:
        self.respond(joke()); return True

    # ── Voice & Persona ───────────────────────────────────────────────────────
    def _cmd_voice_female(self, q, ql) -> bool:
        self.respond(voice.switch_voice("female")); return True

    def _cmd_voice_male(self, q, ql) -> bool:
        self.respond(voice.switch_voice("male")); return True

    def _cmd_voice_mute(self, q, ql) -> bool:
        self.respond(voice.toggle_voice(False)); return True

    def _cmd_voice_enable(self, q, ql) -> bool:
        self.respond(voice.toggle_voice(True)); return True

    def _cmd_persona_friday(self, q, ql) -> bool:
        voice.switch_voice("female")
        self.assistant_name = "FRIDAY"
        self.respond(f"Switching to F.R.I.D.A.Y. persona. Female intelligence suite active, {self.user_name}.")
        return True

    def _cmd_persona_jarvis(self, q, ql) -> bool:
        voice.switch_voice("male")
        self.assistant_name = "JARVIS"
        self.respond(f"J.A.R.V.I.S. persona restored. Good to be back, {self.user_name}.")
        return True

    # ── Mode Switching ────────────────────────────────────────────────────────
    def _cmd_mode_text(self, q, ql) -> bool:
        self.mode = "text"
        self.respond("Switched to Text-Only mode. Voice recognition paused.")
        return True

    def _cmd_mode_voice(self, q, ql) -> bool:
        self.mode = "voice"
        self.respond("Switched to Voice-Only mode. Microphone is now active.")
        return True

    def _cmd_mode_hybrid(self, q, ql) -> bool:
        self.mode = "hybrid"
        self.respond("Switched to Hybrid mode. Both voice and text input are active.")
        return True

    # ── AI Brain ──────────────────────────────────────────────────────────────
    def _cmd_ask_ai(self, q, ql) -> bool:
        prompt = ql.replace("ask jarvis", "").replace("ask ai", "").strip()
        if not prompt:
            self.respond("Please specify what you would like me to reason about, Sir.")
            return True
        return self._query_brain(q, prompt)

    def _cmd_ai_fallback(self, q, ql) -> bool:
        """Gemini handles anything not matched by the local registry."""
        return self._query_brain(q, q)

    def _cmd_open_generic(self, q, ql) -> bool:
        target = ql.replace("open", "", 1).strip()
        self.respond(open_custom_website_or_app(target))
        return True

    # ── Internal ──────────────────────────────────────────────────────────────
    def _query_brain(self, raw_query: str, prompt: str) -> bool:
        if not self.brain.available:
            msg = search_google(raw_query)
            self.respond(
                f"My AI reasoning module is offline. I've searched Google for '{raw_query}' instead."
            )
            return True
        print_thinking()
        reply = self.brain.ask(prompt)
        self.respond(reply, is_llm=True)
        return True


# ══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="J.A.R.V.I.S. — Just A Rather Very Intelligent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-t", "--text",   action="store_true", help="Text-only mode (no microphone)")
    parser.add_argument("-v", "--voice",  action="store_true", help="Voice-only mode (no keyboard input)")
    parser.add_argument("--friday",       action="store_true", help="Start with F.R.I.D.A.Y. female persona")
    parser.add_argument("--test",         type=str,            help="Execute a single test command and exit")
    args = parser.parse_args()

    mode = "text" if args.text else "voice" if args.voice else "hybrid"
    assistant = JarvisAssistant(mode=mode)

    if args.friday:
        voice.switch_voice("female")
        assistant.assistant_name = "FRIDAY"

    if args.test:
        print_status("TEST", f"Executing: '{args.test}'", HIGHLIGHT)
        result = assistant.execute_command(args.test)
        print_status("TEST", f"Result: {'CONTINUE' if result else 'EXIT'}", SUCCESS)
        return

    assistant.run()


if __name__ == "__main__":
    main()
