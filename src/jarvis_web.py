"""
jarvis_web.py — JARVIS Web Application Backend & Server
========================================================
FastAPI + WebSocket + Uvicorn server providing:
  - Real-time bidirectional WebSocket telemetry and command streaming
  - Full REST API suite for telemetry, commands, memory, weather, news, system actions
  - Static file delivery for the Sci-Fi holographic HUD interface
"""

from __future__ import annotations

import os
import sys
import json
import asyncio
import argparse
import webbrowser
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure src in sys.path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from config import CONFIG, save_config, BASE_DIR, WEB_DIR, STATIC_DIR
from logger import log
from jarvis_core import JarvisCore, CommandResult
from core.voice_engine import voice
from services.weather_service import get_weather
from services.news import fetch_headlines
from services.system_control import take_screenshot, change_volume, lock_screen
from services.app_launcher import open_custom_website_or_app

# ── Core Assistant Singleton ───────────────────────────────────────────────────
core = JarvisCore(mode="hybrid")

# ── FastAPI App Setup ──────────────────────────────────────────────────────────
app = FastAPI(
    title="J.A.R.V.I.S. Personal AI Assistant",
    version=JarvisCore.VERSION,
    description="Production-grade AI Assistant Web Backend and Holographic HUD",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Request Models ────────────────────────────────────────────────────
class CommandRequest(BaseModel):
    query: str
    speak: bool = True


class NoteCreateRequest(BaseModel):
    text: str
    category: str = "general"


class SystemActionRequest(BaseModel):
    action: str
    target: Optional[str] = None


class ConfigUpdateRequest(BaseModel):
    user_name: Optional[str] = None
    assistant_name: Optional[str] = None
    voice_gender: Optional[str] = None
    speech_rate: Optional[int] = None
    speech_volume: Optional[float] = None
    voice_enabled: Optional[bool] = None
    persona: Optional[str] = None


# ── WebSocket Connection Manager ───────────────────────────────────────────────
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        log.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            log.info(f"WebSocket client disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast_json(self, data: Dict[str, Any]) -> None:
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception as exc:
                log.warning(f"Error sending to client: {exc}")
                self.disconnect(connection)


manager = ConnectionManager()


# ── Background Telemetry Task ──────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event() -> None:
    async def telemetry_loop():
        while True:
            try:
                if manager.active_connections:
                    telemetry = core.get_telemetry()
                    await manager.broadcast_json({
                        "type": "telemetry",
                        "data": telemetry
                    })
            except Exception as exc:
                log.error(f"Telemetry broadcast loop error: {exc}")
            await asyncio.sleep(1.5)

    asyncio.create_task(telemetry_loop())
    log.info("JARVIS Web Server background telemetry task started.")


# ── REST Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/status")
async def get_status() -> Dict[str, Any]:
    return {
        "status": "online",
        "telemetry": core.get_telemetry()
    }


@app.post("/api/command")
async def execute_command(req: CommandRequest) -> Dict[str, Any]:
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    await manager.broadcast_json({"type": "state", "state": "THINKING"})
    result = core.execute(req.query, speak_aloud=req.speak)
    new_state = "SPEAKING" if (req.speak and result.spoken and voice.enabled) else "IDLE"
    await manager.broadcast_json({"type": "state", "state": new_state})

    await manager.broadcast_json({
        "type": "command_result",
        "query": req.query,
        "result": result.to_dict()
    })

    return {
        "query": req.query,
        "result": result.to_dict()
    }


@app.get("/api/notes")
async def list_notes() -> List[Dict[str, Any]]:
    return core.get_notes()


@app.post("/api/notes")
async def create_note(req: NoteCreateRequest) -> Dict[str, Any]:
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Note text cannot be empty.")
    note = core.add_note(req.text, req.category)
    return {"success": True, "note": note}


@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int) -> Dict[str, Any]:
    success = core.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found.")
    return {"success": True, "deleted_id": note_id}


@app.post("/api/notes/clear")
async def clear_all_notes() -> Dict[str, Any]:
    core.purge_notes()
    return {"success": True, "message": "All notes cleared."}


@app.get("/api/weather")
async def get_weather_data() -> Dict[str, Any]:
    return get_weather()


@app.get("/api/news")
async def get_news_data(category: str = "top", limit: int = 5) -> Dict[str, Any]:
    articles = fetch_headlines(category=category, limit=limit)
    return {"category": category, "articles": articles}


@app.post("/api/system/control")
async def trigger_system_action(req: SystemActionRequest) -> Dict[str, Any]:
    action = req.action.lower()
    if action == "screenshot":
        msg = take_screenshot()
        return {"success": True, "message": msg}
    elif action == "lock":
        msg = lock_screen()
        return {"success": True, "message": msg}
    elif action == "volume_up":
        msg = change_volume("up")
        return {"success": True, "message": msg}
    elif action == "volume_down":
        msg = change_volume("down")
        return {"success": True, "message": msg}
    elif action == "volume_mute":
        msg = change_volume("mute")
        return {"success": True, "message": msg}
    elif action == "launch" and req.target:
        msg = open_custom_website_or_app(req.target)
        return {"success": True, "message": msg}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown system action: {action}")


@app.get("/api/config")
async def get_config() -> Dict[str, Any]:
    return CONFIG.to_dict()


@app.post("/api/config")
async def update_config(req: ConfigUpdateRequest) -> Dict[str, Any]:
    if req.user_name is not None:
        CONFIG.user_name = req.user_name
        core.user_name = req.user_name
        core.brain.user_name = req.user_name
    if req.assistant_name is not None:
        CONFIG.assistant_name = req.assistant_name
        core.assistant_name = req.assistant_name
    if req.voice_gender is not None:
        CONFIG.voice_gender = req.voice_gender
        voice.switch_voice(req.voice_gender)
    if req.speech_rate is not None:
        voice.set_rate(req.speech_rate)
    if req.speech_volume is not None:
        voice.set_volume(req.speech_volume)
    if req.voice_enabled is not None:
        voice.toggle_voice(req.voice_enabled)
    if req.persona is not None:
        if req.persona.upper() == "FRIDAY":
            core._cmd_persona_friday("", "")
        else:
            core._cmd_persona_jarvis("", "")

    save_config(CONFIG)
    return {"success": True, "config": CONFIG.to_dict()}


@app.get("/api/history")
async def get_history() -> List[Dict[str, Any]]:
    return core.history[-50:]


# ── Static File Hosting ────────────────────────────────────────────────────────
STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    fav_file = STATIC_DIR / "favicon.ico"
    if fav_file.exists():
        return FileResponse(str(fav_file))
    return FileResponse(str(STATIC_DIR / "favicon.png"))


@app.get("/")
async def serve_index() -> FileResponse:
    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        return JSONResponse({"error": "Web HUD template not found."}, status_code=404)
    return FileResponse(str(index_file))


# ── Main Entry Point ───────────────────────────────────────────────────────────

def start_server(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> None:
    url = f"http://{host}:{port}"
    print(f"\n========================================================")
    print(f"  J.A.R.V.I.S. Web Application Server")
    print(f"  Interface running at: {url}")
    print(f"  WebSocket endpoint : ws://{host}:{port}/ws")
    print(f"========================================================\n")

    if open_browser:
        def _launch_browser():
            import time
            time.sleep(1.2)
            try:
                webbrowser.open_new_tab(url)
            except Exception:
                pass
        import threading
        threading.Thread(target=_launch_browser, daemon=True).start()

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS Web Application HUD")
    parser.add_argument("--host", default="127.0.0.1", help="Server host address")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    start_server(host=args.host, port=args.port, open_browser=not args.no_browser)
