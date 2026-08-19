# 🏛️ J.A.R.V.I.S. Architecture Documentation

**Just A Rather Very Intelligent System — Production Architecture Guide**

---

## 📐 High-Level Architecture Overview

JARVIS is built on a decoupled, multi-tier modular architecture where all user-facing interfaces (Interactive CLI, Voice Loop, and the Futuristic Web Application HUD) share a unified core engine:

```mermaid
graph TD
    subgraph UI_Layer [Client & Interface Layer]
        WebHUD["🌐 Holographic Web HUD\n(HTML5, Canvas, Web Speech API, Vanilla CSS/JS)"]
        CLI["💻 Terminal Console & Voice Loop\n(colorama, SpeechRecognition, pyttsx3)"]
    end

    subgraph Server_Layer [FastAPI Async Server (src/jarvis_web.py)]
        FastAPIApp[FastAPI Web Server]
        WSEndpoint["WebSocket (/ws)\nLive Telemetry (1.5s interval) & Command Stream"]
        RESTEndpoints["REST API (/api/*)\nStatus, Command, Notes, Weather, News, Control, Config"]
    end

    subgraph Core_Layer [Core Assistant Controller (src/jarvis_core.py)]
        JarvisCore["JarvisCore Engine\nPriority Intent Dispatcher"]
        NotesManager["Memory & Notes Manager\n(data/notes.json)"]
    end

    subgraph Subsystems_Layer [Subsystems & Services]
        AIBrain["Multi-Tier AI Brain (src/core/ai_brain.py)\nTier 1: Google Gemini API\nTier 2: Direct Wikipedia REST Synthesizer"]
        VoiceEngine["Async TTS Engine (src/core/voice_engine.py)\nBackground Worker Queue + Persona Switching"]
        Telemetry["System Telemetry (src/services/system_control.py)\nCPU, RAM, Disk, Battery, Network, Workstation Lock"]
        AppLauncher["App Launcher (src/services/app_launcher.py)\nDesktop Apps, YouTube & Deep Search"]
        Services["Weather & News (src/services/)\nOpen-Meteo, IP Geolocation, RSS Headlines"]
    end

    WebHUD <--> WSEndpoint
    WebHUD <--> RESTEndpoints
    WSEndpoint --> FastAPIApp
    RESTEndpoints --> FastAPIApp
    FastAPIApp --> JarvisCore
    CLI --> JarvisCore

    JarvisCore --> AIBrain
    JarvisCore --> VoiceEngine
    JarvisCore --> Telemetry
    JarvisCore --> AppLauncher
    JarvisCore --> Services
    JarvisCore --> NotesManager
```

---

## 📁 Directory Structure Breakdown

```
c:\Jarvis/
├── src/                          # Central Python package
│   ├── __init__.py
│   ├── jarvis_core.py            # Central coordinator & intent router
│   ├── jarvis_web.py             # FastAPI & WebSocket backend
│   ├── config.py                 # Configuration manager & path resolutions
│   ├── logger.py                 # Structured logger with UUID session tracking
│   ├── ui.py                     # Terminal UI & Diagnostics
│   ├── core/                     # Intelligence & Audio
│   │   ├── __init__.py
│   │   ├── ai_brain.py           # Multi-tier AI Brain (Gemini + Wikipedia REST)
│   │   └── voice_engine.py       # Thread-safe async TTS queue
│   ├── services/                 # External APIs & OS integration
│   │   ├── __init__.py
│   │   ├── system_control.py     # Hardware telemetry, volume & OS automation
│   │   ├── app_launcher.py       # Desktop apps & deep search launcher
│   │   ├── weather_service.py    # Geolocation & Open-Meteo forecast
│   │   └── news.py               # Live RSS news headlines
│   └── modules/                  # Utilities & features
│       ├── __init__.py
│       ├── helpers.py            # Notes, command capture, jokes
│       ├── diction.py            # Offline dictionary
│       ├── OCR.py                # Computer vision / OCR
│       ├── youtube_downloader.py # Media fetcher
│       └── amazon.py             # Amazon search helper
│
├── web/                          # Futuristic Holographic Web HUD Frontend
│   ├── index.html                # Responsive Sci-Fi cockpit
│   └── static/
│       ├── css/style.css         # Glassmorphism dark theme & animations
│       └── js/app.js             # WebSocket client, Canvas Arc Reactor & Web Speech
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md           # Architecture design
│   ├── API_REFERENCE.md          # REST & WebSocket API specs
│   └── COMMANDS.md               # Built-in command reference
│
├── assets/                       # Static media, images & packages
│   ├── images/
│   └── packages/                 # Wheels (.whl)
│
├── data/                         # Persistent database & config
│   ├── data.json                 # Dictionary database
│   ├── notes.json                # Memory notes store
│   └── config.json               # Assistant preferences
│
├── logs/                         # Daily rotating log files
├── jarvis.py                     # Root CLI & Web runner
├── launch_jarvis_web.bat         # 1-click Windows Web HUD launcher
├── launch_jarvis_cli.bat         # 1-click Windows CLI launcher
├── requirements.txt              # Production Python dependencies
└── README.md                     # Main project overview
```

---

## ⚡ Core Design Principles

1. **Non-Blocking Execution**: Voice synthesis is handled on a dedicated background worker queue, preventing UI/WebSocket thread starvation.
2. **Graceful Degradation**: If Google Gemini API is unavailable or rate-limited (429 quota exhaustion), the AI Brain automatically synthesizes responses using direct Wikipedia REST queries and local lexicon knowledge.
3. **Responsive Everywhere**: Web HUD adapts seamlessly across Mobile devices (320px–767px), Tablets/iPads (768px–1023px), Laptops (1024px–1366px), and 4K Ultra-wide Desktops.
