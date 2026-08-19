"""
src/services/__init__.py — Hardware diagnostics, app launching, weather, news services
"""

from .system_control import (
    get_system_stats, take_screenshot, change_volume,
    lock_screen, get_time_and_date, get_network_info
)
from .app_launcher import (
    open_whatsapp, open_vscode, open_spotify, open_calculator,
    open_notepad, open_terminal, open_file_explorer, open_task_manager,
    search_youtube, search_google, open_url, open_custom_website_or_app
)
from .weather_service import get_weather, get_location
from .news import fetch_headlines, speak_news

__all__ = [
    "get_system_stats", "take_screenshot", "change_volume",
    "lock_screen", "get_time_and_date", "get_network_info",
    "open_whatsapp", "open_vscode", "open_spotify", "open_calculator",
    "open_notepad", "open_terminal", "open_file_explorer", "open_task_manager",
    "search_youtube", "search_google", "open_url", "open_custom_website_or_app",
    "get_weather", "get_location", "fetch_headlines", "speak_news"
]
