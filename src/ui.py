"""
ui.py — JARVIS Terminal UI & Visual Diagnostics
=================================================
Rich terminal output with colorama:
  - Startup banner with session ID & timestamp
  - Full system diagnostics
  - Dedicated styles for LLM / Gemini responses
  - Startup self-test status printer
"""

import os
import sys
import socket
import platform
import datetime
import psutil
from colorama import init, Fore, Back, Style

# Windows stdout encoding fix
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
LLM_CLR   = Fore.LIGHTCYAN_EX + Style.BRIGHT

W = 72


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _line(char: str = "═", color: str = PRIMARY) -> str:
    return color + char * W


def _center(text: str, color: str = PRIMARY) -> str:
    return color + text.center(W)


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
    print(MUTED + "  [*] Web Application HUD  Active")
    print(MUTED + "  [*] System Telemetry     Active")
    print(_line("═") + "\n")


def print_diagnostics() -> None:
    cpu      = psutil.cpu_percent(interval=0.2)
    ram      = psutil.virtual_memory()
    disk     = psutil.disk_usage("/")
    battery  = psutil.sensors_battery()

    bat_str  = "AC Power" if not battery else f"{battery.percent:.0f}%"
    disk_str = f"{disk.percent:.1f}% used  ({disk.free // (1024**3)} GB free)"
    ram_str  = f"{ram.percent:.1f}%  ({ram.used // (1024**3):.1f} / {ram.total // (1024**3):.1f} GB)"

    try:
        hostname = socket.gethostname()
        ip_addr  = socket.gethostbyname(hostname)
    except Exception:
        ip_addr  = "Unavailable"

    print(MUTED + "┌─ SYSTEM DIAGNOSTICS " + "─" * (W - 22))
    print(MUTED + f"│  CPU     : {PRIMARY}{cpu}%")
    print(MUTED + f"│  RAM     : {PRIMARY}{ram_str}")
    print(MUTED + f"│  Disk    : {PRIMARY}{disk_str}")
    print(MUTED + f"│  Battery : {PRIMARY}{bat_str}")
    print(MUTED + f"│  IP      : {PRIMARY}{ip_addr}")
    print(MUTED + "└" + "─" * (W - 1) + "\n")


def print_jarvis_response(msg: str) -> None:
    print(f"\n{PRIMARY}[JARVIS]{TEXT}  {msg}\n")


def print_llm_response(msg: str) -> None:
    print(f"\n{LLM_CLR}[JARVIS/AI]{TEXT}  {msg}\n")


def print_thinking() -> None:
    print(f"{MUTED}[AI]  Reasoning...", end="\r", flush=True)


def print_info(msg: str) -> None:
    print(f"{SECONDARY}[INFO]{TEXT}  {msg}")


def print_warning(msg: str) -> None:
    print(f"{WARNING}[WARN]{TEXT}  {msg}")


def print_error(msg: str) -> None:
    print(f"{ERROR_CLR}[ERROR]{TEXT}  {msg}")


def print_status(tag: str, msg: str, color: str = PRIMARY) -> None:
    print(f"{color}[{tag.upper()}]{TEXT}  {msg}")


def print_listening() -> None:
    print(f"{SECONDARY}[MIC]{TEXT}  Listening... (speak clearly or press Enter to type)")


def print_recognizing() -> None:
    print(f"{SECONDARY}[MIC]{TEXT}  Recognizing audio...")


def print_user_input(text: str, source: str = "Voice") -> None:
    print(f"\n{HIGHLIGHT}[{source.upper()}]{TEXT} {text}")


def print_selftest_header() -> None:
    print(MUTED + "┌─ STARTUP SELF-TEST " + "─" * (W - 21))


def print_selftest_footer() -> None:
    print(MUTED + "└" + "─" * (W - 1) + "\n")


def print_module_status(module: str, ok: bool, detail: str = "") -> None:
    badge = f"{SUCCESS}[OK] " if ok else f"{ERROR_CLR}[FAIL]"
    dtl   = f"{MUTED}  {detail}" if detail else ""
    print(MUTED + f"│  {badge} {TEXT}{module:<22}{dtl}")


def print_session_end(command_count: int, start_time: datetime.datetime) -> None:
    duration = datetime.datetime.now() - start_time
    m, s = divmod(int(duration.total_seconds()), 60)
    print("\n" + _line("─", MUTED))
    print(MUTED + f"  Session Duration : {TEXT}{m}m {s}s")
    print(MUTED + f"  Commands Handled : {TEXT}{command_count}")
    print(_line("═") + "\n")


def print_help() -> None:
    print("\n" + _line("═"))
    print(_center("JARVIS COMMAND CHEATSHEET"))
    print(_line("─", MUTED))
    cmds = [
        ("AI / Brain", "who is [X], explain [topic], tell me about [X]"),
        ("System",     "cpu, system stats, ram, battery, screenshot, lock pc"),
        ("Hardware",   "volume up, volume down, mute, network info"),
        ("Launcher",   "open vscode, open spotify, open whatsapp, open terminal"),
        ("Media",      "play [song] on youtube, search youtube for [query]"),
        ("Search",     "search google for [query], open github, open chatgpt"),
        ("Live Info",  "weather, top news, define [word], tell me a joke"),
        ("Notes",      "note down [text], read notes, clear notes"),
        ("Voice",      "switch to friday, switch to jarvis, female voice, mute voice"),
        ("Modes",      "text mode, voice mode, hybrid mode, exit / shutdown"),
    ]
    for cat, ex in cmds:
        print(f"  {PRIMARY}{cat:<12}{TEXT}: {ex}")
    print(_line("═") + "\n")
