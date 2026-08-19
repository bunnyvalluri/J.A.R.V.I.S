"""
jarvis_core.py — JARVIS Central Controller & Intelligence Engine
=================================================================
Lead Engineer: Production-Grade AI Assistant
Version: 2.0 Pro

Architecture:
  - Decoupled, thread-safe core assistant engine used by both CLI and Web UI
  - Priority intent dispatcher with structured command responses
  - System telemetry collector (CPU, RAM, Disk, Battery, Network, Uptime)
  - Notes & Memory manager
  - Persona switching (JARVIS / FRIDAY)
  - Voice TTS and Gemini AI Brain integration
"""

from __future__ import annotations

import os
import sys
import datetime
import socket
import psutil
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List, Tuple, Callable

# Ensure src in sys.path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import CONFIG, save_config, DATA_FILE, NOTES_FILE, SCREENSHOTS_DIR
from logger import log, get_session_id
from core.voice_engine import speak, voice
from core.ai_brain import GeminiBrain
from services.weather_service import get_weather
from services.news import fetch_headlines
from services.system_control import (
    get_system_stats, take_screenshot, change_volume,
    lock_screen, get_time_and_date, get_network_info
)
from services.app_launcher import (
    open_whatsapp, open_vscode, open_spotify, open_calculator,
    open_notepad, open_terminal, open_file_explorer, open_task_manager,
    search_youtube, search_google, open_url, open_custom_website_or_app
)
from modules.helpers import joke, translate, save_note, read_notes, clear_notes, _load_notes, _save_notes


@dataclass
class CommandResult:
    """Structured response for any executed command."""
    success: bool
    text: str
    spoken: str
    category: str
    data: Optional[Dict[str, Any]] = None
    should_exit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JarvisCore:
    """
    Core JARVIS assistant controller.
    Thread-safe and decoupled from UI display layers.
    """

    VERSION = "2.0 Pro"

    def __init__(self, mode: str = "hybrid") -> None:
        self.mode = mode
        self.session_id = get_session_id()
        self.start_time = datetime.datetime.now()
        self.command_count = 0
        self.history: List[Dict[str, Any]] = []

        # Load preferences from CONFIG
        self.user_name = CONFIG.user_name
        self.assistant_name = CONFIG.assistant_name
        self.persona = "JARVIS"

        # Initialize AI Brain
        self.brain = GeminiBrain(user_name=self.user_name)

        # Build routes
        self._routes: List[Tuple[Callable[[str], bool], Callable[[str, str], CommandResult]]] = []
        self._register_routes()

        log.info(f"JarvisCore initialized — session={self.session_id}, user={self.user_name}")

    # ── Telemetry & Diagnostics ────────────────────────────────────────────────

    def get_telemetry(self) -> Dict[str, Any]:
        """Fetch comprehensive live system metrics."""
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        battery = psutil.sensors_battery()
        boot_ts = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime_delta = datetime.datetime.now() - boot_ts
        uptime_str = str(uptime_delta).split(".")[0]

        bat_pct = round(battery.percent) if battery else 100
        bat_plugged = battery.power_plugged if battery else True

        try:
            hostname = socket.gethostname()
            ip_addr = socket.gethostbyname(hostname)
        except Exception:
            hostname = "LocalHost"
            ip_addr = "127.0.0.1"

        return {
            "version": self.VERSION,
            "assistant_name": self.assistant_name,
            "user_name": self.user_name,
            "persona": self.persona,
            "mode": self.mode,
            "uptime": uptime_str,
            "session_id": self.session_id,
            "command_count": self.command_count,
            "cpu_percent": cpu,
            "ram_percent": ram.percent,
            "ram_used_gb": round(ram.used / (1024**3), 1),
            "ram_total_gb": round(ram.total / (1024**3), 1),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "battery_percent": bat_pct,
            "battery_charging": bat_plugged,
            "hostname": hostname,
            "ip_address": ip_addr,
            "voice_enabled": voice.enabled,
            "voice_gender": CONFIG.voice_gender,
            "speech_rate": CONFIG.speech_rate,
            "brain_status": "ONLINE" if self.brain.available else "LOCAL_REASONING",
            "brain_source": getattr(self.brain, "last_source", "Ready"),
        }

    # ── Route Registration ─────────────────────────────────────────────────────

    def _register_routes(self) -> None:
        """Register all deterministic intent matchers and handlers."""
        def r(matcher: Callable[[str], bool], handler: Callable[[str, str], CommandResult]):
            self._routes.append((matcher, handler))

        # System & Lifecycle
        r(lambda q: q in {"exit", "quit", "stop", "sleep", "goodbye", "bye", "shutdown"}, self._cmd_exit)
        r(lambda q: q in {"help", "what can you do", "commands", "show commands"}, self._cmd_help)
        r(lambda q: q in {"hi", "hello", "hey", "hola", "namaste", "greetings"}, self._cmd_greet)
        r(lambda q: "how are you" in q, self._cmd_status)
        r(lambda q: "who are you" in q or "your name" in q, self._cmd_identity)
        r(lambda q: "who made you" in q or "who created you" in q, self._cmd_creator)
        r(lambda q: "are you there" in q or "are you online" in q, self._cmd_ping)
        r(lambda q: "thank you" in q or q == "thanks", self._cmd_thanks)

        # Persona & Voice settings
        r(lambda q: "switch to friday" in q or "friday mode" in q, self._cmd_persona_friday)
        r(lambda q: "switch to jarvis" in q or "jarvis mode" in q, self._cmd_persona_jarvis)
        r(lambda q: "female voice" in q, self._cmd_voice_female)
        r(lambda q: "male voice" in q, self._cmd_voice_male)
        r(lambda q: "mute voice" in q or "disable voice" in q or "silence" in q, self._cmd_voice_mute)
        r(lambda q: "enable voice" in q or "unmute voice" in q, self._cmd_voice_enable)

        # Modes
        r(lambda q: "text mode" in q or "switch to text" in q, self._cmd_mode_text)
        r(lambda q: "voice mode" in q or "switch to voice" in q, self._cmd_mode_voice)
        r(lambda q: "hybrid mode" in q or "switch to hybrid" in q, self._cmd_mode_hybrid)

        # Hardware & System Controls
        r(lambda q: any(k in q for k in ("system stats", "cpu", "ram", "memory usage", "battery", "hardware")), self._cmd_sysinfo)
        r(lambda q: "screenshot" in q or "take screenshot" in q or "capture screen" in q, self._cmd_screenshot)
        r(lambda q: "volume up" in q or "increase volume" in q, self._cmd_vol_up)
        r(lambda q: "volume down" in q or "decrease volume" in q, self._cmd_vol_down)
        r(lambda q: "mute" in q or "unmute" in q, self._cmd_mute)
        r(lambda q: "lock screen" in q or "lock workstation" in q or q == "lock pc", self._cmd_lock)
        r(lambda q: any(k in q for k in ("time", "current time", "date", "today")), self._cmd_time)
        r(lambda q: "ip address" in q or "network info" in q or q == "my ip", self._cmd_network)

        # App Launchers & Quick Links
        r(lambda q: "whatsapp" in q, self._cmd_whatsapp)
        r(lambda q: "vscode" in q or "vs code" in q or q == "open code", self._cmd_vscode)
        r(lambda q: "spotify" in q, self._cmd_spotify)
        r(lambda q: "calculator" in q or q == "calc", self._cmd_calculator)
        r(lambda q: "notepad" in q, self._cmd_notepad)
        r(lambda q: "terminal" in q or "powershell" in q or "command prompt" in q, self._cmd_terminal)
        r(lambda q: "task manager" in q, self._cmd_task_manager)
        r(lambda q: "file explorer" in q or q == "open files", self._cmd_explorer)

        # Web & Search
        r(lambda q: q == "open youtube", self._cmd_open_youtube)
        r(lambda q: q == "open google", self._cmd_open_google)
        r(lambda q: q == "open github", self._cmd_open_github)
        r(lambda q: "open chatgpt" in q, self._cmd_open_chatgpt)
        r(lambda q: "open stackoverflow" in q, self._cmd_open_so)
        r(lambda q: q == "open amazon", self._cmd_open_amazon)
        r(lambda q: "play" in q and "youtube" in q, self._cmd_play_youtube)
        r(lambda q: q.startswith("search youtube for "), self._cmd_search_youtube)
        r(lambda q: q.startswith("search google for ") or q.startswith("search for "), self._cmd_search_google)
        r(lambda q: q.startswith("google "), self._cmd_google)

        # Weather & News
        r(lambda q: any(k in q for k in ("weather", "temperature", "forecast", "climate")), self._cmd_weather)
        r(lambda q: any(k in q for k in ("news", "headlines", "top stories")), self._cmd_news)

        # Notes & Memory
        r(lambda q: q.startswith("remember that ") or q.startswith("note down ") or q.startswith("save note "), self._cmd_save_note)
        r(lambda q: "what did i ask" in q or "read notes" in q or "show notes" in q or "my notes" in q, self._cmd_read_notes)
        r(lambda q: "clear notes" in q or "delete notes" in q or "forget notes" in q, self._cmd_clear_notes)

        # Dictionary & Fun
        r(lambda q: q.startswith("define ") or q.startswith("meaning of ") or "dictionary" in q, self._cmd_define)
        r(lambda q: "joke" in q or "tell me a joke" in q, self._cmd_joke)

        # Generic open
        r(lambda q: q.startswith("open "), self._cmd_open_generic)

    # ── Execution Pipeline ─────────────────────────────────────────────────────

    def execute(self, query: str, mode_override: Optional[str] = None, speak_aloud: bool = True) -> CommandResult:
        """
        Execute a command string through priority routing or AI fallback.
        """
        if not query or not query.strip():
            return CommandResult(
                success=True,
                text="Standing by, Sir.",
                spoken="Standing by, Sir.",
                category="system"
            )

        raw_query = query.strip()
        q = raw_query.lower()
        self.command_count += 1

        now_iso = datetime.datetime.now().isoformat()
        self.history.append({"role": "user", "text": raw_query, "ts": now_iso})

        # Match routes
        res: Optional[CommandResult] = None
        for matcher, handler in self._routes:
            try:
                if matcher(q):
                    log.info(f"JarvisCore: Matched route {handler.__name__} for '{raw_query[:60]}'")
                    res = handler(raw_query, q)
                    break
            except Exception as exc:
                log.error(f"JarvisCore: Route error in {handler.__name__}: {exc}")
                continue

        # AI Fallback if no deterministic route matched
        if res is None:
            log.info(f"JarvisCore: Routing to AI Brain — '{raw_query[:60]}'")
            ai_reply = self.brain.ask(raw_query)
            res = CommandResult(
                success=True,
                text=ai_reply,
                spoken=ai_reply,
                category="ai_brain",
                data={"source": getattr(self.brain, "last_source", "AI")}
            )

        # Store response in history
        self.history.append({
            "role": "assistant",
            "text": res.text,
            "category": res.category,
            "ts": datetime.datetime.now().isoformat()
        })

        # Speak if requested and enabled
        if speak_aloud and res.spoken and voice.enabled:
            speak(res.spoken, block=False)

        return res

    # ── Notes & Memory Management ──────────────────────────────────────────────

    def get_notes(self) -> List[Dict[str, Any]]:
        """Retrieve all stored notes."""
        return _load_notes()

    def add_note(self, text: str, category: str = "general") -> Dict[str, Any]:
        """Add a new note with timestamp."""
        notes = _load_notes()
        new_id = (max(n.get("id", 0) for n in notes) + 1) if notes else 1
        new_note = {
            "id": new_id,
            "text": text.strip(),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "category": category
        }
        notes.append(new_note)
        _save_notes(notes)
        log.info(f"JarvisCore: Saved note #{new_id}: '{text[:40]}'")
        return new_note

    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID."""
        notes = _load_notes()
        filtered = [n for n in notes if n.get("id") != note_id]
        if len(filtered) < len(notes):
            _save_notes(filtered)
            log.info(f"JarvisCore: Deleted note #{note_id}")
            return True
        return False

    def purge_notes(self) -> bool:
        """Clear all stored notes."""
        return _save_notes([])

    # ── Command Handlers ───────────────────────────────────────────────────────

    def _cmd_exit(self, q: str, ql: str) -> CommandResult:
        elapsed = datetime.datetime.now() - self.start_time
        mins = int(elapsed.total_seconds() // 60)
        msg = f"Goodbye, {self.user_name}. Session lasted {mins} minute{'s' if mins != 1 else ''}. All systems powering down."
        return CommandResult(success=True, text=msg, spoken=msg, category="system", should_exit=True)

    def _cmd_help(self, q: str, ql: str) -> CommandResult:
        msg = (
            "Available capabilities include: System diagnostics ('cpu', 'system stats'), "
            "App launching ('open vscode', 'whatsapp', 'spotify'), Media ('play [song] on youtube'), "
            "Information ('weather', 'news', 'define [word]'), Memory ('note down [text]', 'read notes'), "
            "and AI queries ('who is Albert Einstein')."
        )
        return CommandResult(success=True, text=msg, spoken="Here is my core capability list, Sir.", category="help")

    def _cmd_greet(self, q: str, ql: str) -> CommandResult:
        msg = f"Hello, {self.user_name}. How may I assist you today?"
        return CommandResult(success=True, text=msg, spoken=msg, category="social")

    def _cmd_status(self, q: str, ql: str) -> CommandResult:
        msg = f"All systems are functioning at peak efficiency, {self.user_name}. Thank you for asking."
        return CommandResult(success=True, text=msg, spoken=msg, category="social")

    def _cmd_identity(self, q: str, ql: str) -> CommandResult:
        msg = f"I am {self.assistant_name} — Just A Rather Very Intelligent System, version {self.VERSION}."
        return CommandResult(success=True, text=msg, spoken=msg, category="social")

    def _cmd_creator(self, q: str, ql: str) -> CommandResult:
        msg = "I was engineered as a production-grade personal AI desktop assistant."
        return CommandResult(success=True, text=msg, spoken=msg, category="social")

    def _cmd_ping(self, q: str, ql: str) -> CommandResult:
        msg = f"Always present and standing by, {self.user_name}."
        return CommandResult(success=True, text=msg, spoken=msg, category="social")

    def _cmd_thanks(self, q: str, ql: str) -> CommandResult:
        msg = f"You are most welcome, {self.user_name}. It is my pleasure to assist."
        return CommandResult(success=True, text=msg, spoken=msg, category="social")

    # ── Persona & Voices ───────────────────────────────────────────────────────

    def _cmd_persona_friday(self, q: str, ql: str) -> CommandResult:
        self.persona = "FRIDAY"
        self.assistant_name = "FRIDAY"
        voice.switch_voice("female")
        msg = "F.R.I.D.A.Y. persona activated. Good to be with you, Sir."
        return CommandResult(success=True, text=msg, spoken=msg, category="persona")

    def _cmd_persona_jarvis(self, q: str, ql: str) -> CommandResult:
        self.persona = "JARVIS"
        self.assistant_name = "JARVIS"
        voice.switch_voice("male")
        msg = "J.A.R.V.I.S. persona activated. Standing by, Sir."
        return CommandResult(success=True, text=msg, spoken=msg, category="persona")

    def _cmd_voice_female(self, q: str, ql: str) -> CommandResult:
        res = voice.switch_voice("female")
        return CommandResult(success=True, text=res, spoken=res, category="voice")

    def _cmd_voice_male(self, q: str, ql: str) -> CommandResult:
        res = voice.switch_voice("male")
        return CommandResult(success=True, text=res, spoken=res, category="voice")

    def _cmd_voice_mute(self, q: str, ql: str) -> CommandResult:
        res = voice.toggle_voice(False)
        return CommandResult(success=True, text=res, spoken=res, category="voice")

    def _cmd_voice_enable(self, q: str, ql: str) -> CommandResult:
        res = voice.toggle_voice(True)
        return CommandResult(success=True, text=res, spoken=res, category="voice")

    # ── Modes ─────────────────────────────────────────────────────────────────

    def _cmd_mode_text(self, q: str, ql: str) -> CommandResult:
        self.mode = "text"
        CONFIG.default_mode = "text"
        save_config(CONFIG)
        msg = "Text mode activated, Sir. Microphone input paused."
        return CommandResult(success=True, text=msg, spoken=msg, category="mode")

    def _cmd_mode_voice(self, q: str, ql: str) -> CommandResult:
        self.mode = "voice"
        CONFIG.default_mode = "voice"
        save_config(CONFIG)
        msg = "Voice mode activated, Sir. Listening continuously."
        return CommandResult(success=True, text=msg, spoken=msg, category="mode")

    def _cmd_mode_hybrid(self, q: str, ql: str) -> CommandResult:
        self.mode = "hybrid"
        CONFIG.default_mode = "hybrid"
        save_config(CONFIG)
        msg = "Hybrid mode activated, Sir. Both voice and text are active."
        return CommandResult(success=True, text=msg, spoken=msg, category="mode")

    # ── System Control ─────────────────────────────────────────────────────────

    def _cmd_sysinfo(self, q: str, ql: str) -> CommandResult:
        spoken, display = get_system_stats()
        text = f"CPU: {display['cpu']} | RAM: {display['ram']} | Disk: {display['disk']} | Battery: {display['battery']}"
        return CommandResult(success=True, text=text, spoken=spoken, category="system_stats", data=display)

    def _cmd_screenshot(self, q: str, ql: str) -> CommandResult:
        res = take_screenshot()
        return CommandResult(success=True, text=res, spoken=res, category="screenshot")

    def _cmd_vol_up(self, q: str, ql: str) -> CommandResult:
        res = change_volume("up")
        return CommandResult(success=True, text=res, spoken=res, category="hardware")

    def _cmd_vol_down(self, q: str, ql: str) -> CommandResult:
        res = change_volume("down")
        return CommandResult(success=True, text=res, spoken=res, category="hardware")

    def _cmd_mute(self, q: str, ql: str) -> CommandResult:
        res = change_volume("mute")
        return CommandResult(success=True, text=res, spoken=res, category="hardware")

    def _cmd_lock(self, q: str, ql: str) -> CommandResult:
        res = lock_screen()
        return CommandResult(success=True, text=res, spoken=res, category="security")

    def _cmd_time(self, q: str, ql: str) -> CommandResult:
        res = get_time_and_date()
        return CommandResult(success=True, text=res, spoken=res, category="clock")

    def _cmd_network(self, q: str, ql: str) -> CommandResult:
        res = get_network_info()
        return CommandResult(success=True, text=res, spoken=res, category="network")

    # ── App Launchers ──────────────────────────────────────────────────────────

    def _cmd_whatsapp(self, q: str, ql: str) -> CommandResult:
        res = open_whatsapp()
        return CommandResult(success=True, text=res, spoken=res, category="launcher")

    def _cmd_vscode(self, q: str, ql: str) -> CommandResult:
        res = open_vscode()
        return CommandResult(success=True, text=res, spoken=res, category="launcher")

    def _cmd_spotify(self, q: str, ql: str) -> CommandResult:
        res = open_spotify()
        return CommandResult(success=True, text=res, spoken=res, category="launcher")

    def _cmd_calculator(self, q: str, ql: str) -> CommandResult:
        res = open_calculator()
        return CommandResult(success=True, text=res, spoken=res, category="launcher")

    def _cmd_notepad(self, q: str, ql: str) -> CommandResult:
        res = open_notepad()
        return CommandResult(success=True, text=res, spoken=res, category="launcher")

    def _cmd_terminal(self, q: str, ql: str) -> CommandResult:
        res = open_terminal()
        return CommandResult(success=True, text=res, spoken=res, category="launcher")

    def _cmd_task_manager(self, q: str, ql: str) -> CommandResult:
        res = open_task_manager()
        return CommandResult(success=True, text=res, spoken=res, category="launcher")

    def _cmd_explorer(self, q: str, ql: str) -> CommandResult:
        res = open_file_explorer()
        return CommandResult(success=True, text=res, spoken=res, category="launcher")

    # ── Web Shortcuts & Search ─────────────────────────────────────────────────

    def _cmd_open_youtube(self, q: str, ql: str) -> CommandResult:
        open_url("https://youtube.com")
        return CommandResult(success=True, text="Opening YouTube, Sir.", spoken="Opening YouTube, Sir.", category="web")

    def _cmd_open_google(self, q: str, ql: str) -> CommandResult:
        open_url("https://google.com")
        return CommandResult(success=True, text="Opening Google, Sir.", spoken="Opening Google, Sir.", category="web")

    def _cmd_open_github(self, q: str, ql: str) -> CommandResult:
        open_url("https://github.com")
        return CommandResult(success=True, text="Opening GitHub, Sir.", spoken="Opening GitHub, Sir.", category="web")

    def _cmd_open_chatgpt(self, q: str, ql: str) -> CommandResult:
        open_url("https://chatgpt.com")
        return CommandResult(success=True, text="Opening ChatGPT, Sir.", spoken="Opening ChatGPT, Sir.", category="web")

    def _cmd_open_so(self, q: str, ql: str) -> CommandResult:
        open_url("https://stackoverflow.com")
        return CommandResult(success=True, text="Opening Stack Overflow, Sir.", spoken="Opening Stack Overflow, Sir.", category="web")

    def _cmd_open_amazon(self, q: str, ql: str) -> CommandResult:
        open_url("https://amazon.com")
        return CommandResult(success=True, text="Opening Amazon, Sir.", spoken="Opening Amazon, Sir.", category="web")

    def _cmd_play_youtube(self, q: str, ql: str) -> CommandResult:
        track = ql.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
        track = track or "top music"
        res = search_youtube(track)
        return CommandResult(success=True, text=res, spoken=res, category="media")

    def _cmd_search_youtube(self, q: str, ql: str) -> CommandResult:
        query = ql.replace("search youtube for", "").strip()
        res = search_youtube(query)
        return CommandResult(success=True, text=res, spoken=res, category="media")

    def _cmd_search_google(self, q: str, ql: str) -> CommandResult:
        query = ql.replace("search google for", "").replace("search for", "").strip()
        res = search_google(query)
        return CommandResult(success=True, text=res, spoken=res, category="search")

    def _cmd_google(self, q: str, ql: str) -> CommandResult:
        query = ql.replace("google", "", 1).strip()
        res = search_google(query)
        return CommandResult(success=True, text=res, spoken=res, category="search")

    def _cmd_open_generic(self, q: str, ql: str) -> CommandResult:
        target = ql.replace("open", "", 1).strip()
        res = open_custom_website_or_app(target)
        return CommandResult(success=True, text=res, spoken=res, category="launcher")

    # ── Weather & News ────────────────────────────────────────────────────────

    def _cmd_weather(self, q: str, ql: str) -> CommandResult:
        w = get_weather()
        text = w.get("display", "Weather data unavailable.")
        spoken = w.get("spoken", "Weather data is currently unavailable, Sir.")
        return CommandResult(success=w.get("success", False), text=text, spoken=spoken, category="weather", data=w)

    def _cmd_news(self, q: str, ql: str) -> CommandResult:
        articles = fetch_headlines(limit=CONFIG.max_news_headlines)
        if not articles:
            return CommandResult(
                success=False,
                text="Unable to retrieve headlines at this time.",
                spoken="I am unable to retrieve today's headlines at the moment, Sir.",
                category="news"
            )
        lines = [f"{i}. {a['title']}" for i, a in enumerate(articles, 1)]
        text = "Top Headlines:\n" + "\n".join(lines)
        spoken = f"Here are today's top {len(articles)} headlines, Sir: " + "; ".join(a['title'] for a in articles[:3])
        return CommandResult(success=True, text=text, spoken=spoken, category="news", data={"articles": articles})

    # ── Memory & Notes ────────────────────────────────────────────────────────

    def _cmd_save_note(self, q: str, ql: str) -> CommandResult:
        for prefix in ["remember that ", "note down ", "save note "]:
            if ql.startswith(prefix):
                note_content = q[len(prefix):].strip()
                res = save_note(note_content)
                return CommandResult(success=True, text=res, spoken=res, category="notes")
        res = save_note(q)
        return CommandResult(success=True, text=res, spoken=res, category="notes")

    def _cmd_read_notes(self, q: str, ql: str) -> CommandResult:
        res = read_notes()
        return CommandResult(success=True, text=res, spoken=res, category="notes", data={"notes": _load_notes()})

    def _cmd_clear_notes(self, q: str, ql: str) -> CommandResult:
        res = clear_notes()
        return CommandResult(success=True, text=res, spoken=res, category="notes")

    # ── Dictionary & Jokes ────────────────────────────────────────────────────

    def _cmd_define(self, q: str, ql: str) -> CommandResult:
        word = ql.replace("define", "").replace("meaning of", "").replace("dictionary", "").strip()
        res = translate(word)
        return CommandResult(success=True, text=res, spoken=res, category="dictionary")

    def _cmd_joke(self, q: str, ql: str) -> CommandResult:
        j = joke()
        return CommandResult(success=True, text=j, spoken=j, category="humor")
