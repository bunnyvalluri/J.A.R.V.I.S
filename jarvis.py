"""
jarvis.py — Root J.A.R.V.I.S. Personal AI Assistant Entry Point
===============================================================
Lead Engineer: Production-Grade AI Assistant
Version: 2.0 Pro

Supports:
  - Interactive CLI / Voice Console (default): `python jarvis.py`
  - Holographic Web Application HUD: `python jarvis.py --web`
  - Text-Only / Voice-Only / Persona Flags: `python jarvis.py --text`, `python jarvis.py --friday`
  - Single Instruction Diagnostic Test: `python jarvis.py --test "..."`
"""

from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path

# Add src to Python path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import CONFIG, save_config
from logger import log, get_session_id
from ui import (
    print_banner, print_diagnostics, print_jarvis_response,
    print_llm_response, print_info, print_error, print_status,
    print_session_end, print_selftest_header, print_selftest_footer,
    print_module_status, HIGHLIGHT, SUCCESS
)
from core.voice_engine import speak, voice
from modules.helpers import takeCommand
from jarvis_core import JarvisCore, CommandResult


# ── Self-Test Diagnostic ───────────────────────────────────────────────────────

def run_selftest(core: JarvisCore) -> dict:
    """Run startup health check on all subsystems."""
    results = {}

    try:
        results["Voice Engine"] = (voice.engine is not None)
    except Exception:
        results["Voice Engine"] = False

    try:
        import speech_recognition as sr
        sr.Microphone()
        results["Microphone"] = True
    except Exception:
        results["Microphone"] = False

    try:
        from services.weather_service import get_weather
        results["Weather Service"] = True
    except Exception:
        results["Weather Service"] = False

    try:
        from services.news import fetch_headlines
        results["News Feed"] = True
    except Exception:
        results["News Feed"] = False

    results["Gemini AI Brain"] = core.brain.available

    try:
        from config import LOG_DIR
        results["Log System"] = LOG_DIR.exists()
    except Exception:
        results["Log System"] = False

    try:
        import fastapi
        import uvicorn
        results["Web Application HUD"] = True
    except Exception:
        results["Web Application HUD"] = False

    return results


# ── Interactive CLI Assistant ──────────────────────────────────────────────────

class JarvisCLI:
    """Terminal & Voice interface runner powered by JarvisCore."""

    def __init__(self, mode: str = "hybrid") -> None:
        self.core = JarvisCore(mode=mode)
        self.user_name = self.core.user_name
        self.assistant_name = self.core.assistant_name
        self.mode = mode

    def wish_me(self) -> None:
        import datetime
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            greeting = f"Good morning, {self.user_name}."
        elif 12 <= hour < 18:
            greeting = f"Good afternoon, {self.user_name}."
        else:
            greeting = f"Good evening, {self.user_name}."
        msg = f"{greeting} I am {self.assistant_name}, version {self.core.VERSION}. All systems are fully operational and standing by."
        print_jarvis_response(msg)
        speak(msg, block=False)

    def run(self) -> None:
        """Main interaction loop."""
        print_banner(version=self.core.VERSION, user=self.user_name, session_id=self.core.session_id)
        print_diagnostics()

        # Startup Diagnostics Self-Test
        test_results = run_selftest(self.core)
        print_selftest_header()
        for module, ok in test_results.items():
            detail = ""
            if module == "Gemini AI Brain":
                detail = "Gemini client linked" if ok else "Operating via Knowledge Synthesizer fallback"
            print_module_status(module, ok, detail)
        print_selftest_footer()

        self.wish_me()
        print_info(
            f"Mode: [{self.mode.upper()}]  |  "
            f"AI Brain: {'ONLINE' if self.core.brain.available else 'LOCAL KNOWLEDGE'}  |  "
            f"Type 'help' for commands, 'exit' to quit."
        )
        print()

        while True:
            try:
                query = takeCommand(mode=self.mode)
                if query:
                    result = self.core.execute(query, speak_aloud=True)
                    if result.category == "ai_brain":
                        print_llm_response(result.text)
                    else:
                        print_jarvis_response(result.text)

                    if result.should_exit:
                        break

            except KeyboardInterrupt:
                print("\n")
                msg = f"Keyboard interrupt detected. Shutting down, {self.user_name}."
                print_jarvis_response(msg)
                speak(msg, block=True)
                break
            except Exception as exc:
                log.error(f"Main CLI loop error: {exc}", exc_info=True)
                print_error(f"Unexpected error: {exc}")

        print_session_end(self.core.command_count, self.core.start_time)
        log.info(f"CLI Session ended — commands={self.core.command_count}")


# ── Main Entry Point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="J.A.R.V.I.S. — Just A Rather Very Intelligent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-w", "--web",    action="store_true", help="Launch the Futuristic Web Application HUD")
    parser.add_argument("-t", "--text",   action="store_true", help="Text-only mode (no microphone)")
    parser.add_argument("-v", "--voice",  action="store_true", help="Voice-only mode (continuous microphone)")
    parser.add_argument("--friday",       action="store_true", help="Start with F.R.I.D.A.Y. female persona")
    parser.add_argument("--test",         type=str,            help="Execute a single test command and exit")
    parser.add_argument("--port",         type=int, default=8000, help="Web server port (when running --web)")
    args = parser.parse_args()

    # Web HUD Mode
    if args.web:
        from jarvis_web import start_server
        if args.friday:
            CONFIG.voice_gender = "female"
            CONFIG.assistant_name = "FRIDAY"
        start_server(port=args.port, open_browser=True)
        return

    mode = "text" if args.text else "voice" if args.voice else "hybrid"
    cli = JarvisCLI(mode=mode)

    if args.friday:
        cli.core._cmd_persona_friday("", "")

    if args.test:
        print_status("TEST", f"Executing: '{args.test}'", HIGHLIGHT)
        res = cli.core.execute(args.test, speak_aloud=False)
        print_status("TEST", f"Response: {res.text}", SUCCESS)
        return

    cli.run()


if __name__ == "__main__":
    main()
