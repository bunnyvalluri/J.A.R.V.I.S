<div align="center">

# 🤖 J.A.R.V.I.S — Production-Grade Personal AI Assistant & Holographic Web HUD

**Just A Rather Very Intelligent System — A Modular, Multi-Modal Python Voice, Automation & Web Application Assistant Powered by Google Gemini & Resilient Local Intelligence**

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![WebSockets](https://img.shields.io/badge/WebSockets-Realtime%20Telemetry-010101?style=for-the-badge&logo=socketdotio&logoColor=white)](#)
[![Platform Support](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/bunnyvalluri/J.A.R.V.I.S)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br/>

<img src="jarvis1.jpg" alt="JARVIS Banner" width="800" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.4);"/>

<br/>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-web-application-hud">Web Application HUD</a> •
  <a href="#-key-features">Key Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-execution-modes">Execution Modes</a> •
  <a href="#-command-reference">Command Reference</a> •
  <a href="#-api-endpoints">API Endpoints</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-contributing">Contributing</a>
</p>

</div>

---

## 🌟 Overview

**J.A.R.V.I.S (Version 2.0 Pro)** is a production-grade personal artificial intelligence assistant built in Python. Engineered with high resilience, modular architecture, and extensible command pipelines, it seamlessly unifies:
1. **Futuristic Sci-Fi Web Application HUD**: An Iron-Man style holographic dashboard with live animated Arc Reactor, real-time telemetry gauges, in-browser Web Speech voice recognition, chat terminal, and memory vault.
2. **Interactive CLI & Voice Console**: Non-blocking offline TTS voice synthesis (`pyttsx3`), speech recognition (`SpeechRecognition`), and diagnostic terminal output.
3. **Multi-Tier AI Brain**: Powered by the official Google GenAI SDK (`google.genai`) with automatic model fallback chaining and an intelligent Knowledge Synthesizer fallback for resilient offline/quota reasoning.

---

## 🌐 Web Application HUD

Launch the web interface instantly with:
```bash
python jarvis.py --web
# or double-click launch_jarvis_web.bat
```

### ✨ Web HUD Highlights:
- **Holographic Arc Reactor Visualizer**: HTML5 Canvas animation with dynamic state transitions (`IDLE`, `LISTENING`, `THINKING`, `SPEAKING`).
- **Live Hardware Telemetry**: Real-time dials & animated gauges for CPU load, RAM usage, storage capacity, battery status, and network IP streamed via WebSockets.
- **In-Browser Web Speech API**: One-click microphone voice input with speech-to-text preview and auto-submission.
- **Command Launcher Matrix**: One-click quick launchers for VS Code, Spotify, WhatsApp, Terminal, File Explorer, Calculator, Screenshots, and Screen Lock.
- **Live Atmosphere & Intelligence**: Atmospheric weather card with hyper-local metrics and live categorized news feeds (Top, Tech, World).
- **Interactive Memory Vault**: Add, search, delete, and manage persistent timestamped memory notes.
- **System Configuration Modal**: Runtime customization for user designation, persona (JARVIS / FRIDAY), speech rate, and volume.

---

## ✨ Key Features

<table>
  <tr>
    <td width="50%">
      <h3>🧠 Multi-Tier AI Brain</h3>
      <ul>
        <li><b>Google Gemini API:</b> Automatic model fallback chaining across <code>gemini-2.5-flash</code>, <code>gemini-flash-latest</code>, and <code>gemini-pro-latest</code>.</li>
        <li><b>Knowledge Synthesizer Fallback:</b> Automatically synthesizes answers using Wikipedia REST archives, local dictionaries, and system telemetry when offline or quota-limited.</li>
        <li><b>Session Memory:</b> Multi-turn rolling conversation history.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🎙️ Multi-Modal Interaction</h3>
      <ul>
        <li><b>Web Speech API + Microphone:</b> In-browser voice control alongside desktop speech recognition.</li>
        <li><b>Dual Persona Switcher:</b> Instant runtime toggle between <b>J.A.R.V.I.S</b> (Male) and <b>F.R.I.D.A.Y</b> (Female).</li>
        <li><b>Non-Blocking Async Voice:</b> Thread-safe background TTS queue ensures UI and web loops never freeze.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>⚡ System Telemetry & Control</h3>
      <ul>
        <li><b>Hardware Health:</b> Real-time monitoring of CPU load, RAM, storage, and battery percentage.</li>
        <li><b>OS Operations:</b> Volume controls (up/down/mute), workstation lock, and local IP diagnostics.</li>
        <li><b>Automated Screenshots:</b> Instant screen capture archived to <code>Pictures/JARVIS_Screenshots</code>.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🚀 App Launcher & Web Automation</h3>
      <ul>
        <li><b>Desktop Apps:</b> One-command launch for VS Code, Terminal, WhatsApp, Spotify, Notepad, and Calculator.</li>
        <li><b>Deep Search Routing:</b> Instant query redirection for Google, YouTube, ChatGPT, GitHub, and Stack Overflow.</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🏛️ Architecture

```
J.A.R.V.I.S/
├── jarvis.py                 # Core CLI & Web entry point (supports --web, --text, --voice, --test)
├── jarvis_core.py            # Decoupled JarvisCore central controller & priority dispatcher
├── jarvis_web.py             # FastAPI backend with WebSocket telemetry & REST API endpoints
├── ai_brain.py               # Resilient Multi-Tier AI Brain (Gemini + Knowledge Synthesizer)
├── voice_engine.py           # Thread-safe async singleton TTS engine with speech queue
├── system_control.py         # Hardware telemetry, volume & OS automation
├── app_launcher.py           # Desktop application & web URL orchestrator
├── weather_service.py        # Geolocation & weather forecasting service
├── news.py                   # RSS headline aggregator
├── helpers.py                # Speech recognition, JSON notes engine & dictionary
├── ui.py                     # Rich terminal styling, diagnostic banners & self-test
├── config.py                 # Type-safe AppConfig dataclass, .env loader & config.json manager
├── logger.py                 # Structured daily rotating session logger & UUID tagging
├── web/                      # Futuristic Holographic Web HUD Frontend
│   ├── index.html            # Sci-Fi HTML5 Dashboard Layout
│   └── static/
│       ├── css/style.css     # Glassmorphic dark theme, animations & cyber HUD styling
│       └── js/app.js         # WebSocket client, Canvas Arc Reactor & Web Speech controller
├── launch_jarvis_web.bat     # One-click Windows launcher for Web HUD
├── launch_jarvis_cli.bat     # One-click Windows launcher for Terminal Console
├── requirements.txt          # Production Python dependencies
├── .env.example              # Template for API keys and environment variables
└── config.json               # Persistent user preferences & configuration
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/bunnyvalluri/J.A.R.V.I.S.git
cd J.A.R.V.I.S

# Install production dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure your API key (optional for local knowledge mode):

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Execution

```bash
# Option A: Launch Futuristic Web Application HUD (Recommended)
python jarvis.py --web
# or double-click launch_jarvis_web.bat

# Option B: Launch Interactive Terminal CLI Console
python jarvis.py
# or double-click launch_jarvis_cli.bat
```

---

## 🎮 Execution Modes

```bash
# 1. Futuristic Web HUD (FastAPI Server + Browser Dashboard)
python jarvis.py --web

# 2. Standard Hybrid CLI (Microphone Voice + Terminal Command Input)
python jarvis.py

# 3. Text-Only CLI (Keyboard input only)
python jarvis.py --text

# 4. Voice-Only CLI (Hands-free continuous microphone recognition)
python jarvis.py --voice

# 5. Persona Preset (Launch directly with F.R.I.D.A.Y. female voice profile)
python jarvis.py --friday

# 6. Non-Interactive Command Test (Executes a single instruction and exits)
python jarvis.py --test "what is the time"
python jarvis.py --test "system stats"
```

---

## 🔌 API Endpoints (Web Backend)

When running `python jarvis.py --web`, the FastAPI server exposes:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Serves the Holographic Web HUD interface |
| `/ws` | `WebSocket` | Real-time bidirectional telemetry & command stream |
| `/api/status` | `GET` | Real-time hardware telemetry and subsystem statuses |
| `/api/command` | `POST` | Execute natural language commands (`{"query": "...", "speak": true}`) |
| `/api/notes` | `GET`, `POST` | Retrieve or add timestamped memory notes |
| `/api/notes/{id}`| `DELETE` | Delete a specific note |
| `/api/weather` | `GET` | Hyper-local weather data |
| `/api/news` | `GET` | Live RSS headlines by category (`top`, `tech`, `world`, `india`) |
| `/api/system/control` | `POST` | Hardware actions (`screenshot`, `lock`, `volume_up`, `launch`) |
| `/api/config` | `GET`, `POST` | View or update assistant configuration |

---

## 📖 Command Reference

| Category | Example Voice / Typed Commands | Action Performed |
| :--- | :--- | :--- |
| **AI Brain** | `who is Albert Einstein`, `explain quantum computing` | Queries Gemini with fallback to Wikipedia Knowledge Synthesizer |
| **System** | `cpu status`, `system stats`, `battery`, `ram` | Real-time CPU, RAM, Disk, and Power diagnostics |
| **System** | `take screenshot`, `capture screen` | Saves full screenshot to `Pictures/JARVIS_Screenshots` |
| **System** | `volume up`, `volume down`, `mute`, `unmute` | Adjusts master system audio level |
| **System** | `lock screen`, `lock workstation`, `lock pc` | Secures the active OS desktop session |
| **Apps** | `open vscode`, `open code` | Launches Visual Studio Code workspace |
| **Apps** | `open whatsapp`, `open spotify` | Opens native app or web equivalent |
| **Apps** | `open calculator`, `open notepad`, `open terminal` | Opens native utility and terminal windows |
| **Web & Info** | `play interstellar soundtrack on youtube` | Launches YouTube media stream |
| **Web & Info** | `search google for quantum physics` | Opens targeted Google search |
| **Live Data** | `what is the weather`, `current temperature` | Reports hyper-local weather conditions |
| **Live Data** | `today's news`, `top headlines` | Reads top curated RSS news updates aloud |
| **Productivity** | `note down meeting at 4 PM`, `read notes` | Stores and reads persistent JSON memory |
| **Persona** | `switch to friday`, `switch to jarvis` | Changes assistant voice and identity on the fly |

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
