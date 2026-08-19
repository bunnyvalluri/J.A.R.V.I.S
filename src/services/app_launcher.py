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
        if os.name == "nt":
            subprocess.Popen(f'start "" "{url}"', shell=True)
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
        return "Opening WhatsApp for you, Sir.", None
    except Exception:
        pass
    open_url("https://web.whatsapp.com")
    return "Opening WhatsApp Web in your browser, Sir.", "https://web.whatsapp.com"


def open_vscode():
    """Open Visual Studio Code dynamically."""
    try:
        res = subprocess.run(["code", "--version"], capture_output=True, text=True, shell=True)
        if res.returncode == 0:
            subprocess.Popen(["code"], shell=True)
            return "Opening Visual Studio Code, Sir.", None
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
            return "Opening Visual Studio Code, Sir.", None

    return "VS Code executable not found on standard paths, Sir.", None


def open_spotify():
    """Open Spotify application or web player."""
    try:
        os.system("start spotify:")
        return "Opening Spotify, Sir.", None
    except Exception:
        open_url("https://open.spotify.com")
        return "Opening Spotify Web Player, Sir.", "https://open.spotify.com"


def open_calculator():
    """Launch Windows Calculator."""
    try:
        subprocess.Popen("calc.exe")
        return "Opening Calculator, Sir.", None
    except Exception as e:
        return f"Unable to open Calculator: {e}", None


def open_notepad():
    """Launch Notepad."""
    try:
        subprocess.Popen("notepad.exe")
        return "Opening Notepad, Sir.", None
    except Exception as e:
        return f"Unable to open Notepad: {e}", None


def open_terminal():
    """Launch Windows Terminal / PowerShell."""
    try:
        subprocess.Popen("powershell.exe")
        return "Opening PowerShell Terminal, Sir.", None
    except Exception as e:
        return f"Unable to open Terminal: {e}", None


def open_file_explorer(path=None):
    """Open Windows File Explorer."""
    try:
        if path and os.path.exists(path):
            os.startfile(path)
        else:
            subprocess.Popen("explorer.exe")
        return "Opening File Explorer, Sir.", None
    except Exception as e:
        return f"Unable to open File Explorer: {e}", None


def open_task_manager():
    """Launch Task Manager."""
    try:
        subprocess.Popen("taskmgr.exe")
        return "Opening Task Manager, Sir.", None
    except Exception as e:
        return f"Unable to open Task Manager: {e}", None


def search_youtube(query):
    """Search YouTube for a specific query."""
    q = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={q}"
    open_url(url)
    return f"Searching YouTube for '{query}', Sir.", url


def search_google(query):
    """Search Google for a specific query."""
    q = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={q}"
    open_url(url)
    return f"Here is what I found on Google for '{query}', Sir.", url


def open_camera():
    """Launch Windows Camera."""
    try:
        os.system("start microsoft.windows.camera:")
        return "Opening Camera, Sir.", None
    except Exception as e:
        return f"Unable to open Camera: {e}", None


def open_settings():
    """Launch Windows Settings."""
    try:
        os.system("start ms-settings:")
        return "Opening Windows Settings, Sir.", None
    except Exception as e:
        return f"Unable to open Settings: {e}", None


def open_paint():
    """Launch Paint."""
    try:
        subprocess.Popen("mspaint.exe")
        return "Opening Paint, Sir.", None
    except Exception as e:
        return f"Unable to open Paint: {e}", None


def open_custom_website_or_app(target):
    """Intelligent launcher matching common aliases, apps, and generic web URLs."""
    t = target.lower().strip()
    
    # Strip common filler phrases
    for prefix in ["open ", "launch ", "start ", "goto ", "go to ", "browse ", "the ", "can you open ", "please open "]:
        if t.startswith(prefix):
            t = t[len(prefix):].strip()
    for suffix in [" open", " please", " launch", " app", " website", " site"]:
        if t.endswith(suffix):
            t = t[:-len(suffix)].strip()

    APP_MAP = {
        "youtube": ("https://youtube.com", "Opening YouTube, Sir."),
        "google": ("https://google.com", "Opening Google, Sir."),
        "facebook": ("https://facebook.com", "Opening Facebook, Sir."),
        "fb": ("https://facebook.com", "Opening Facebook, Sir."),
        "instagram": ("https://instagram.com", "Opening Instagram, Sir."),
        "insta": ("https://instagram.com", "Opening Instagram, Sir."),
        "github": ("https://github.com", "Opening GitHub, Sir."),
        "chatgpt": ("https://chatgpt.com", "Opening ChatGPT, Sir."),
        "openai": ("https://chatgpt.com", "Opening ChatGPT, Sir."),
        "gemini": ("https://gemini.google.com", "Opening Google Gemini, Sir."),
        "claude": ("https://claude.ai", "Opening Claude AI, Sir."),
        "whatsapp": ("https://web.whatsapp.com", "Opening WhatsApp, Sir."),
        "telegram": ("https://web.telegram.org", "Opening Telegram, Sir."),
        "discord": ("https://discord.com/app", "Opening Discord, Sir."),
        "spotify": ("https://open.spotify.com", "Opening Spotify, Sir."),
        "netflix": ("https://netflix.com", "Opening Netflix, Sir."),
        "prime": ("https://primevideo.com", "Opening Amazon Prime Video, Sir."),
        "primevideo": ("https://primevideo.com", "Opening Amazon Prime Video, Sir."),
        "hotstar": ("https://hotstar.com", "Opening Disney+ Hotstar, Sir."),
        "disney": ("https://hotstar.com", "Opening Disney+ Hotstar, Sir."),
        "reddit": ("https://reddit.com", "Opening Reddit, Sir."),
        "linkedin": ("https://linkedin.com", "Opening LinkedIn, Sir."),
        "twitter": ("https://x.com", "Opening Twitter/X, Sir."),
        "x": ("https://x.com", "Opening Twitter/X, Sir."),
        "gmail": ("https://mail.google.com", "Opening Gmail, Sir."),
        "mail": ("https://mail.google.com", "Opening Gmail, Sir."),
        "drive": ("https://drive.google.com", "Opening Google Drive, Sir."),
        "docs": ("https://docs.google.com", "Opening Google Docs, Sir."),
        "sheets": ("https://sheets.google.com", "Opening Google Sheets, Sir."),
        "slides": ("https://slides.google.com", "Opening Google Slides, Sir."),
        "maps": ("https://maps.google.com", "Opening Google Maps, Sir."),
        "weather": ("https://weather.com", "Opening Weather, Sir."),
        "stackoverflow": ("https://stackoverflow.com", "Opening Stack Overflow, Sir."),
        "amazon": ("https://amazon.com", "Opening Amazon, Sir."),
        "wikipedia": ("https://wikipedia.org", "Opening Wikipedia, Sir."),
        "wiki": ("https://wikipedia.org", "Opening Wikipedia, Sir."),
        "pinterest": ("https://pinterest.com", "Opening Pinterest, Sir."),
        "tiktok": ("https://tiktok.com", "Opening TikTok, Sir."),
        "twitch": ("https://twitch.tv", "Opening Twitch, Sir."),
        "canva": ("https://canva.com", "Opening Canva, Sir."),
        "notion": ("https://notion.so", "Opening Notion, Sir."),
        "figma": ("https://figma.com", "Opening Figma, Sir."),
        "bing": ("https://bing.com", "Opening Bing, Sir.")
    }

    if t in APP_MAP:
        url, msg = APP_MAP[t]
        open_url(url)
        return msg, url

    # Desktop Application Checks
    if "whatsapp" in t:
        return open_whatsapp()
    elif "vscode" in t or "vs code" in t or t == "code":
        return open_vscode()
    elif "spotify" in t:
        return open_spotify()
    elif "calculator" in t or "calc" in t:
        return open_calculator()
    elif "notepad" in t:
        return open_notepad()
    elif "camera" in t:
        return open_camera()
    elif "paint" in t:
        return open_paint()
    elif "settings" in t:
        return open_settings()
    elif "terminal" in t or "cmd" in t or "powershell" in t:
        return open_terminal()
    elif "explorer" in t or "files" in t or "my computer" in t:
        return open_file_explorer()
    elif "task manager" in t or "taskmgr" in t:
        return open_task_manager()

    if "." in t and not " " in t:
        url = t if t.startswith("http") else f"https://{t}"
        open_url(url)
        return f"Opening {t}, Sir.", url

    return search_google(target)
