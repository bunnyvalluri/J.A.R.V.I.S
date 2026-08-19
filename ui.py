import os
import sys
import platform
import psutil
from colorama import init, Fore, Back, Style

# Ensure stdout supports unicode or safely handles characters on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Initialize colorama
init(autoreset=True)

# Theme Palette
PRIMARY = Fore.CYAN + Style.BRIGHT
SECONDARY = Fore.BLUE + Style.BRIGHT
SUCCESS = Fore.GREEN + Style.BRIGHT
WARNING = Fore.YELLOW + Style.BRIGHT
ERROR = Fore.RED + Style.BRIGHT
MUTED = Fore.LIGHTBLACK_EX
HIGHLIGHT = Fore.MAGENTA + Style.BRIGHT
TEXT = Fore.WHITE + Style.BRIGHT

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner(version="2.0 Pro", user="Sir"):
    print("\n" + PRIMARY + "=" * 70)
    print(PRIMARY + "          J A R V I S   A I   A S S I S T A N T   O N L I N E")
    print(MUTED + f"          Version {version} | User: {user} | Status: " + SUCCESS + "OPERATIONAL")
    print(PRIMARY + "=" * 70)
    print(MUTED + "  * Voice Commands Active (Microphone)")
    print(MUTED + "  * Typed Commands Active (Console)")
    print(PRIMARY + "-" * 70 + "\n")

def print_diagnostics():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    bat_str = f"{battery.percent}%" if battery else "AC Power"
    os_name = f"{platform.system()} {platform.release()}"

    print(PRIMARY + "[SYSTEM DIAGNOSTICS]")
    print(MUTED + f"OS: {TEXT}{os_name} {MUTED}| CPU: {TEXT}{cpu}% {MUTED}| RAM: {TEXT}{ram}% {MUTED}| Power: {TEXT}{bat_str}")
    print(PRIMARY + "-" * 70 + "\n")

def print_status(tag, message, color=PRIMARY):
    print(f"{color}[{tag}] {TEXT}{message}")

def print_listening():
    print(f"\n{WARNING}[MIC] Listening... {MUTED}(Speak clearly or press Enter to type){Style.RESET_ALL}")

def print_recognizing():
    print(f"{SECONDARY}[MIC] Recognizing audio...{Style.RESET_ALL}")

def print_user_input(query, input_type="Voice"):
    print(f"{HIGHLIGHT}[USER ({input_type})]: {TEXT}{query}")

def print_jarvis_response(response):
    print(f"{SUCCESS}[JARVIS]: {TEXT}{response}\n")

def print_info(message):
    print(f"{PRIMARY}[INFO] {message}")

def print_warning(message):
    print(f"{WARNING}[WARNING] {message}")

def print_error(message):
    print(f"{ERROR}[ERROR] {message}")

def print_help():
    print(f"\n{PRIMARY}" + "=" * 25 + " [ JARVIS CAPABILITIES ] " + "=" * 25)
    commands = [
        ("App Launcher", "Open WhatsApp, YouTube, VS Code, Spotify, Notepad, Calculator"),
        ("Live Weather", "What's the weather / Current weather update"),
        ("Live News", "Tell me the news / Today's top headlines"),
        ("Web Searches", "Search Google for <query> / Search YouTube for <query>"),
        ("Wikipedia", "Who is <person> / What is <topic> / Wikipedia <topic>"),
        ("System Control", "CPU status / Battery level / Take screenshot / Lock screen"),
        ("Memory & Notes", "Remember that <note> / What did I ask you to remember"),
        ("Dictionary", "Meaning of <word> / Define <word>"),
        ("Voice Control", "Switch to female voice / Switch to male voice / Mute voice"),
        ("Utility", "Time / Date / Tell me a joke / Help / Goodbye / Exit"),
    ]
    for cat, desc in commands:
        print(f"{HIGHLIGHT}{cat:<16}{MUTED} : {TEXT}{desc}")
    print(PRIMARY + "=" * 70 + "\n")
