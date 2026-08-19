"""
ui.py — JARVIS Terminal UI & Visual Diagnostics
=================================================
Rich terminal output with colorama:
  - Professional startup banner with session ID & timestamp
  - Full system diagnostics including disk, network, boot time
  - Dedicated styles for LLM / Gemini responses
  - Startup self-test status printer
  - Session end summary with uptime
"""

import os
import sys
import socket
import platform
import datetime
import psutil
from colorama import init, Fore, Back, Style

# ── Windows stdout encoding fix ────────────────────────────────────────────────
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

init(autoreset=True)

# ── Colour Palette ─────────────────────────────────────────────────────────────
PRIMARY   = Fore.CYAN    + Style.BRIGHT
SECONDARY = Fore.BLUE    + Style.BRIGHT
SUCCESS   = Fore.GREEN   + Style.BRIGHT
WARNING   = Fore.YELLOW  + Style.BRIGHT
ERROR_CLR = Fore.RED     + Style.BRIGHT
MUTED     = Fore.LIGHTBLACK_EX
HIGHLIGHT = Fore.MAGENTA + Style.BRIGHT
TEXT      = Fore.WHITE   + Style.BRIGHT
LLM_CLR   = Fore.LIGHTCYAN_EX + Style.BRIGHT  # Gemini responses

# ── Width constant ─────────────────────────────────────────────────────────────
W = 72


# ── Helpers ────────────────────────────────────────────────────────────────────
def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _line(char: str = "═", color: str = PRIMARY) -> str:
    return color + char * W


def _center(text: str, color: str = PRIMARY) -> str:
    return color + text.center(W)


# ── Banner ─────────────────────────────────────────────────────────────────────
def print_banner(version: str = "2.0 Pro", user: str = "Sir", session_id: str = "--------") -> None:
    now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    py_ver = f"Python {sys.version.split()[0]}"

    print("\n" + _line("═"))
    print(_center("J . A . R . V . I . S"))
    print(_center("Just A Rather Very Intelligent System"))
    print(_line("─", MUTED))
    print(MUTED + f"  Version : {TEXT}{version}{MUTED}      User    : {TEXT}{user}")
    print(MUTED + f"  Session : {TEXT}{session_id}{MUTED}      Started : {TEXT}{now}")
    print(MUTED + f"  Runtime : {TEXT}{py_ver}{MUTED}      Host    : {TEXT}{platform.node()}")
    print(_line("─", MUTED))
    print(MUTED + "  [*] Voice Recognition    Active")
    print(MUTED + "  [*] Text Input           Active")
    print(MUTED + "  [*] System Telemetry     Active")
    print(_line("═") + "\n")


# ── System Diagnostics ─────────────────────────────────────────────────────────
def print_diagnostics() -> None:
    cpu      = psutil.cpu_percent(interval=0.3)
    ram      = psutil.virtual_memory()
    disk     = psutil.disk_usage("/")
    battery  = psutil.sensors_battery()
    boot_ts  = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime   = datetime.datetime.now() - boot_ts
    hours, rem = divmod(int(uptime.total_seconds()), 3600)
    minutes  = rem // 60

    bat_str  = "AC Power" if not battery else f"{battery.percent:.0f}%"
    disk_str = f"{disk.percent:.1f}% used  ({disk.free // (1024**3)} GB free)"
    ram_str  = (
        f"{ram.percent:.1f}%  "
        f"({ram.used // (1024**3):.1f} / {ram.total // (1024**3):.1f} GB)"
    )

    try:
        hostname = socket.gethostname()
        ip_addr  = socket.gethostbyname(hostname)
    except Exception:
        ip_addr  = "Unavailable"

    os_name = f"{platform.system()} {platform.release()} ({platform.machine()})"

    print(PRIMARY + "[SYSTEM DIAGNOSTICS]")
    rows = [
        ("OS",      os_name),
        ("CPU",     f"{cpu:.1f}%"),
        ("RAM",     ram_str),
        ("Disk",    disk_str),
        ("Power",   bat_str),
        ("IP",      ip_addr),
        ("Uptime",  f"{hours}h {minutes}m"),
    ]
    for label, value in rows:
        print(MUTED + f"  {label:<8}: {TEXT}{value}")
    print(_line("─", MUTED) + "\n")


# ── Module Self-Test Status ────────────────────────────────────────────────────
def print_module_status(name: str, ok: bool, detail: str = "") -> None:
    icon   = SUCCESS + "[OK]  " if ok else WARNING + "[--]  "
    detail_str = MUTED + f"  {detail}" if detail else ""
    print(f"  {icon}{TEXT}{name:<22}{detail_str}")


def print_selftest_header() -> None:
    print(PRIMARY + "[STARTUP SELF-TEST]")


def print_selftest_footer() -> None:
    print(_line("─", MUTED) + "\n")


# ── I/O Helpers ────────────────────────────────────────────────────────────────
def print_status(tag: str, message: str, color: str = PRIMARY) -> None:
    print(f"{color}[{tag}] {TEXT}{message}")


def print_listening() -> None:
    print(f"\n{WARNING}[MIC]  Listening... {MUTED}(speak clearly or press Enter to type){Style.RESET_ALL}")


def print_recognizing() -> None:
    print(f"{SECONDARY}[MIC]  Recognizing audio...{Style.RESET_ALL}")


def print_user_input(query: str, input_type: str = "Voice") -> None:
    print(f"\n{HIGHLIGHT}[{input_type.upper()}] {TEXT}{query}")


def print_jarvis_response(response: str) -> None:
    print(f"{SUCCESS}[JARVIS]  {TEXT}{response}\n")


def print_llm_response(response: str) -> None:
    """Styled output for Gemini-generated answers."""
    print(f"{LLM_CLR}[JARVIS/AI]  {TEXT}{response}\n")


def print_thinking() -> None:
    """Displayed while waiting for Gemini."""
    print(f"{MUTED}  ... processing with AI brain ...", end="\r", flush=True)


def print_info(message: str) -> None:
    print(f"{PRIMARY}[INFO]  {message}")


def print_warning(message: str) -> None:
    print(f"{WARNING}[WARN]  {message}")


def print_error(message: str) -> None:
    print(f"{ERROR_CLR}[ERR ]  {message}")


# ── Session Start / End ────────────────────────────────────────────────────────
def print_session_end(commands_processed: int, start_time: datetime.datetime) -> None:
    elapsed   = datetime.datetime.now() - start_time
    total_sec = int(elapsed.total_seconds())
    mins, sec = divmod(total_sec, 60)
    print("\n" + _line("─", MUTED))
    print(MUTED + f"  Session Duration : {TEXT}{mins}m {sec}s")
    print(MUTED + f"  Commands Handled : {TEXT}{commands_processed}")
    print(_line("═") + "\n")


# ── Help Menu ──────────────────────────────────────────────────────────────────
def print_help() -> None:
    print(f"\n{PRIMARY}" + "─" * W)
    print(_center("[ JARVIS CAPABILITIES ]", PRIMARY))
    print(_line("─", MUTED))
    commands = [
        ("App Launcher",   "Open WhatsApp, YouTube, VS Code, Spotify, Notepad, Calculator"),
        ("Live Weather",   "weather  /  current weather  /  what's the temperature"),
        ("Live News",      "news  /  headlines  /  top stories"),
        ("Web Search",     "search google for <query>  /  google <query>"),
        ("YouTube",        "play <song> on youtube  /  search youtube for <query>"),
        ("Wikipedia",      "who is <person>  /  what is <topic>"),
        ("System",         "cpu status  /  battery  /  ram  /  take screenshot"),
        ("Volume",         "volume up  /  volume down  /  mute  /  unmute"),
        ("Memory & Notes", "remember that <note>  /  read notes  /  clear notes"),
        ("Dictionary",     "define <word>  /  meaning of <word>"),
        ("Voice Control",  "female voice  /  male voice  /  mute voice  /  enable voice"),
        ("AI Brain",       "ask jarvis <anything>  /  any unknown query → Gemini AI"),
        ("Utility",        "time  /  date  /  tell me a joke  /  my ip  /  help  /  exit"),
    ]
    for cat, desc in commands:
        print(f"  {HIGHLIGHT}{cat:<18}{MUTED}  {TEXT}{desc}")
    print(_line("═") + "\n")
