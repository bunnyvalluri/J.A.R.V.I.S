"""
system_control.py — Hardware Diagnostics & OS Automation
==========================================================
"""

import os
import sys
import ctypes
import datetime
import psutil
from pathlib import Path

try:
    import pyautogui
except Exception:
    pyautogui = None

# Ensure src in sys.path
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import SCREENSHOTS_DIR
from ui import print_status, print_info, SUCCESS, WARNING, PRIMARY
from logger import log


def get_system_stats():
    """Fetch real-time CPU, RAM, Disk, and Battery diagnostics."""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    try:
        disk = psutil.disk_usage('/')
    except Exception:
        disk = None
    battery = psutil.sensors_battery()

    bat_info = "AC Connected"
    if battery:
        plugged = "Charging" if battery.power_plugged else "Discharging"
        bat_info = f"{battery.percent}% ({plugged})"

    spoken = f"CPU usage is at {cpu} percent. Memory usage is at {ram.percent} percent. Battery is at {bat_info}."
    display = {
        "cpu": f"{cpu}%",
        "ram": f"{ram.percent}% ({round(ram.used / (1024**3), 1)}GB / {round(ram.total / (1024**3), 1)}GB)",
        "disk": f"{disk.percent}% ({round(disk.free / (1024**3), 1)}GB free)" if disk else "N/A",
        "battery": bat_info
    }
    return spoken, display


def take_screenshot():
    """Take a screenshot and save it to the Pictures/JARVIS_Screenshots directory."""
    if not pyautogui:
        return "Screenshot capture is available in local desktop environments, Sir."
    try:
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = SCREENSHOTS_DIR / f"JARVIS_screenshot_{timestamp}.png"
        
        img = pyautogui.screenshot()
        img.save(str(file_path))
        print_status("SCREENSHOT", f"Saved to {file_path}", SUCCESS)
        return f"Screenshot captured successfully and saved to your Pictures folder, Sir."
    except Exception as e:
        return f"Failed to capture screenshot: {e}"


def change_volume(action="up"):
    """Control system audio volume via media keys."""
    if not pyautogui:
        return "Volume adjustment is available in local desktop environments, Sir."
    try:
        if action == "up":
            for _ in range(5):
                pyautogui.press("volumeup")
            return "Volume increased, Sir."
        elif action == "down":
            for _ in range(5):
                pyautogui.press("volumedown")
            return "Volume decreased, Sir."
        elif action == "mute":
            pyautogui.press("volumemute")
            return "Audio muted/unmuted, Sir."
    except Exception as e:
        return f"Unable to adjust volume: {e}"


def lock_screen():
    """Lock the Windows workstation."""
    try:
        if hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32"):
            ctypes.windll.user32.LockWorkStation()
            return "Screen locked, Sir."
        return "Workstation lock is supported on Windows desktop environments, Sir."
    except Exception as e:
        return f"Failed to lock screen: {e}"


def get_time_and_date():
    """Get current time, date, and day."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")
    return f"Sir, it is currently {time_str} on {date_str}."


def get_network_info():
    """Get basic network connection info."""
    try:
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return f"Your local IP address is {ip_address} on host {hostname}."
    except Exception as e:
        return f"Unable to determine network IP: {e}"
