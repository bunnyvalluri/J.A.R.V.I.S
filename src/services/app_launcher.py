"""
app_launcher.py — Desktop App & URL Launcher
=============================================
"""

import os
import sys
import subprocess
import webbrowser
import urllib.parse
from pathlib import Path

# Ensure src in sys.path
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui import print_status, print_info, print_error, SUCCESS, PRIMARY, WARNING


def open_url(url):
    """Open a URL in the user's default web browser."""
    try:
        webbrowser.open_new_tab(url)
        return True
    except Exception as e:
        print_error(f"Failed to open URL {url}: {e}")
        return False


def open_whatsapp():
    """Open WhatsApp Desktop app or fallback to WhatsApp Web."""
    try:
        os.system("start whatsapp:")
        print_status("LAUNCHER", "Opening WhatsApp Application...", SUCCESS)
        return "Opening WhatsApp for you, Sir."
    except Exception:
        pass
    open_url("https://web.whatsapp.com")
    return "Opening WhatsApp Web in your browser, Sir."


def open_vscode():
    """Open Visual Studio Code dynamically."""
    try:
        res = subprocess.run(["code", "--version"], capture_output=True, text=True, shell=True)
        if res.returncode == 0:
            subprocess.Popen(["code"], shell=True)
            return "Opening Visual Studio Code, Sir."
    except Exception:
        pass

    user_home = Path.home()
    possible_paths = [
        user_home / "AppData" / "Local" / "Programs" / "Microsoft VS Code" / "Code.exe",
        Path("C:/Program Files/Microsoft VS Code/Code.exe"),
        Path("C:/Program Files (x86)/Microsoft VS Code/Code.exe"),
    ]
    for p in possible_paths:
        if p.exists():
            os.startfile(str(p))
            return "Opening Visual Studio Code, Sir."

    return "VS Code executable not found on standard paths, Sir."


def open_spotify():
    """Open Spotify application or web player."""
    try:
        os.system("start spotify:")
        return "Opening Spotify, Sir."
    except Exception:
        open_url("https://open.spotify.com")
        return "Opening Spotify Web Player, Sir."


def open_calculator():
    """Launch Windows Calculator."""
    try:
        subprocess.Popen("calc.exe")
        return "Opening Calculator, Sir."
    except Exception as e:
        return f"Unable to open Calculator: {e}"


def open_notepad():
    """Launch Notepad."""
    try:
        subprocess.Popen("notepad.exe")
        return "Opening Notepad, Sir."
    except Exception as e:
        return f"Unable to open Notepad: {e}"


def open_terminal():
    """Launch Windows Terminal / PowerShell."""
    try:
        subprocess.Popen("powershell.exe")
        return "Opening PowerShell Terminal, Sir."
    except Exception as e:
        return f"Unable to open Terminal: {e}"


def open_file_explorer(path=None):
    """Open Windows File Explorer."""
    try:
        if path and os.path.exists(path):
            os.startfile(path)
        else:
            subprocess.Popen("explorer.exe")
        return "Opening File Explorer, Sir."
    except Exception as e:
        return f"Unable to open File Explorer: {e}"


def open_task_manager():
    """Launch Task Manager."""
    try:
        subprocess.Popen("taskmgr.exe")
        return "Opening Task Manager, Sir."
    except Exception as e:
        return f"Unable to open Task Manager: {e}"


def search_youtube(query):
    """Search YouTube for a specific query."""
    q = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={q}"
    open_url(url)
    return f"Searching YouTube for '{query}', Sir."


def search_google(query):
    """Search Google for a specific query."""
    q = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={q}"
    open_url(url)
    return f"Here is what I found on Google for '{query}', Sir."


def open_custom_website_or_app(target):
    """Intelligent launcher matching common aliases and generic web URLs."""
    target = target.lower().strip()
    
    APP_MAP = {
        "youtube": ("https://youtube.com", "Opening YouTube, Sir."),
        "google": ("https://google.com", "Opening Google, Sir."),
        "github": ("https://github.com", "Opening GitHub, Sir."),
        "chatgpt": ("https://chatgpt.com", "Opening ChatGPT, Sir."),
        "stackoverflow": ("https://stackoverflow.com", "Opening Stack Overflow, Sir."),
        "reddit": ("https://reddit.com", "Opening Reddit, Sir."),
        "linkedin": ("https://linkedin.com", "Opening LinkedIn, Sir."),
        "twitter": ("https://x.com", "Opening Twitter/X, Sir."),
        "x": ("https://x.com", "Opening Twitter/X, Sir."),
        "gmail": ("https://mail.google.com", "Opening Gmail, Sir."),
        "amazon": ("https://amazon.com", "Opening Amazon, Sir."),
        "netflix": ("https://netflix.com", "Opening Netflix, Sir."),
        "maps": ("https://maps.google.com", "Opening Google Maps, Sir."),
        "weather": ("https://weather.com", "Opening Weather, Sir.")
    }

    if target in APP_MAP:
        url, msg = APP_MAP[target]
        open_url(url)
        return msg

    if "whatsapp" in target:
        return open_whatsapp()
    elif "vscode" in target or "code" in target:
        return open_vscode()
    elif "spotify" in target:
        return open_spotify()
    elif "calculator" in target or "calc" in target:
        return open_calculator()
    elif "notepad" in target:
        return open_notepad()
    elif "terminal" in target or "cmd" in target or "powershell" in target:
        return open_terminal()
    elif "explorer" in target or "files" in target:
        return open_file_explorer()
    elif "task manager" in target or "taskmgr" in target:
        return open_task_manager()

    if "." in target:
        url = target if target.startswith("http") else f"https://{target}"
        open_url(url)
        return f"Opening {target}, Sir."

    return search_google(target)
