<div align="center">

# 🤖 J.A.R.V.I.S — Production-Grade Desktop AI Assistant

**Just A Rather Very Intelligent System — A Modular, Multi-Modal Python Voice & Automation Assistant Powered by Google Gemini 2.0 Flash**

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform Support](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/bunnyvalluri/J.A.R.V.I.S)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![LLM: Gemini 2.0 Flash](https://img.shields.io/badge/LLM-Gemini%202.0%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](#)

<br/>

<img src="jarvis1.jpg" alt="JARVIS Banner" width="800" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);"/>

<br/>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-key-features">Key Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-execution-modes">Execution Modes</a> •
  <a href="#-command-reference">Command Reference</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-logging--diagnostics">Logging & Diagnostics</a> •
  <a href="#-roadmap">Roadmap</a> •
  <a href="#-contributing">Contributing</a>
</p>

</div>

---

## 🌟 Overview

**J.A.R.V.I.S (Version 2.0 Pro)** is a production-grade personal desktop artificial intelligence assistant built in Python. Engineered with high resilience, modular design, and extensible command architecture, it seamlessly bridges offline text-to-speech synthesis and speech recognition with **Google Gemini 2.0 Flash** conversational reasoning, real-time live telemetry, OS-level automation, and computer vision.

Whether issuing voice commands hands-free through your microphone or executing tasks swiftly via the terminal console, J.A.R.V.I.S dynamically adapts to your workflow with sub-second responsiveness.

---

## ✨ Key Features

<table>
  <tr>
    <td width="50%">
      <h3>🧠 Gemini 2.0 Flash AI Brain</h3>
      <ul>
        <li><b>Context-Aware Intelligence:</b> Uses Google Gemini 2.0 Flash for open-ended queries, reasoning, coding, and complex knowledge.</li>
        <li><b>Session Memory:</b> Rolling conversation history preserves multi-turn context.</li>
        <li><b>Persona Directives:</b> Calibrated system instructions ensure an authentic, polite, and witty JARVIS personality.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🎙️ Multi-Modal Interaction</h3>
      <ul>
        <li><b>Hybrid Input Loop:</b> Seamless simultaneous support for voice dictation and typed terminal commands.</li>
        <li><b>Dual Persona Switcher:</b> Instant runtime toggle between <b>J.A.R.V.I.S</b> (Male) and <b>F.R.I.D.A.Y</b> (Female) voice engines.</li>
        <li><b>Offline Low-Latency TTS:</b> Immediate local voice output powered by <code>pyttsx3</code> with self-healing recovery.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>⚡ System Telemetry & Control</h3>
      <ul>
        <li><b>Hardware Health:</b> Real-time monitoring of CPU load, RAM usage, storage capacity, and battery percentage.</li>
        <li><b>OS Operations:</b> Master audio control (volume up/down/mute), workstation lock, and network IP resolution.</li>
        <li><b>Automated Screenshots:</b> Instant screen capture archived with timestamps to your Pictures directory.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🚀 App Launcher & Web Automation</h3>
      <ul>
        <li><b>Desktop Apps:</b> One-command launch for VS Code, PowerShell / Terminal, WhatsApp, Spotify, Notepad, Task Manager, and Calculator.</li>
        <li><b>Deep Search Routing:</b> Instant query redirection for Google, YouTube, Wikipedia summaries, ChatGPT, GitHub, and Stack Overflow.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🌐 Live Data Services</h3>
      <ul>
        <li><b>Geolocation & Weather:</b> Automatic location detection with hyper-local conditions (temperature, humidity, wind velocity).</li>
        <li><b>Curated News Feeds:</b> Multi-source live headlines via RSS (Google News, BBC World, Times of India).</li>
        <li><b>Intelligent Lexicon:</b> Offline dictionary with phonetic & fuzzy matching auto-correction.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🛡️ Resilience, Logging & Notes</h3>
      <ul>
        <li><b>Session-Tagged Logging:</b> Daily rotating log files (<code>logs/jarvis_YYYYMMDD.log</code>) with unique session UUIDs.</li>
        <li><b>Startup Self-Test:</b> Automated pre-flight validation of all sub-modules upon initialization.</li>
        <li><b>Structured JSON Scratchpad:</b> Timestamped notes with automated migration from legacy storage.</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🏛️ Architecture

```
J.A.R.V.I.S/
├── jarvis.py                 # Core application controller & Priority CommandRegistry
├── ai_brain.py               # Google Gemini 2.0 Flash integration & conversation memory
├── logger.py                 # Structured daily rotating session logger & UUID tagging
├── config.py                 # Type-safe AppConfig dataclass, .env loader & config.json manager
├── voice_engine.py           # Text-to-speech singleton engine & persona manager
├── helpers.py                # Speech recognition, JSON notes engine & dictionary
├── system_control.py         # Hardware telemetry, volume & OS automation
├── app_launcher.py           # Desktop application & web URL orchestrator
├── weather_service.py        # Geolocation & weather forecasting service
├── news.py                   # RSS headline aggregator and speech reader
├── diction.py                # Intelligent dictionary & fuzzy search
├── OCR.py                    # Optical Character Recognition module
├── youtube_downloader.py     # YouTube media fetcher
├── ui.py                     # Rich terminal styling, diagnostic banners & self-test
├── Face-Recognition/         # Computer vision authentication module
├── requirements.txt          # Production Python dependencies
├── .env.example              # Template for API keys and environment variables
└── config.json               # Persistent user preferences & configuration
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python:** 3.9, 3.10, 3.11, 3.12, or 3.13 recommended.
- **Audio:** Working microphone and speaker setup.
- **Gemini API Key:** Free key from [Google AI Studio](https://aistudio.google.com/).

### 2. Installation

Clone the repository and set up your virtual environment:

```bash
# Clone repository
git clone https://github.com/bunnyvalluri/J.A.R.V.I.S.git
cd J.A.R.V.I.S

# Create and activate virtual environment
# Windows:
python -m venv venv
venv\Scripts\activate

# macOS / Linux:
python3 -m venv venv
source venv/bin/activate
```

Install the production dependencies:

```bash
pip install -r requirements.txt
```

> [!TIP]
> **Windows Audio Setup:** If you encounter any installation issues with `PyAudio`, run:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```
> **Linux (Ubuntu/Debian) Users:** Ensure system audio prerequisites are installed:
> ```bash
> sudo apt-get update && sudo apt-get install espeak portaudio19-dev libasound-dev
> ```

### 3. Environment Configuration

Copy `.env.example` to `.env` and insert your Gemini API Key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

---

## 🎮 Execution Modes

Run J.A.R.V.I.S with flexible command-line flags tailored to your setup:

```bash
# 1. Standard Hybrid Mode (Microphone Voice + Terminal Command Input)
python jarvis.py

# 2. Text-Only Mode (Keyboard input only — ideal for quiet environments)
python jarvis.py --text

# 3. Voice-Only Mode (Hands-free continuous microphone recognition)
python jarvis.py --voice

# 4. Persona Preset (Launch directly with F.R.I.D.A.Y. female voice profile)
python jarvis.py --friday

# 5. Non-Interactive Command Test (Executes a single instruction and exits)
python jarvis.py --test "what is the time"
python jarvis.py --test "cpu status"
```

---

## 📖 Command Reference

J.A.R.V.I.S understands natural queries across 40+ built-in intents, falling back seamlessly to **Gemini 2.0 Flash** for open-ended queries:

| Category | Example Voice / Typed Commands | Action Performed |
| :--- | :--- | :--- |
| **AI Brain** | `ask jarvis how does quantum computing work`, `explain recursion` | Queries Gemini 2.0 Flash with multi-turn context |
| **System** | `cpu status`, `system stats`, `battery`, `ram`, `hardware` | Real-time CPU, RAM, Disk, and Power diagnostics |
| **System** | `take screenshot`, `capture screen` | Saves full screenshot to `Pictures/JARVIS_Screenshots` |
| **System** | `volume up`, `volume down`, `mute`, `unmute` | Adjusts master system audio level |
| **System** | `lock screen`, `lock workstation`, `lock pc` | Secures the active OS desktop session |
| **Apps** | `open vscode`, `open code` | Launches Visual Studio Code workspace |
| **Apps** | `open whatsapp`, `open spotify` | Opens native app or web equivalent |
| **Apps** | `open calculator`, `open notepad`, `open terminal` | Opens native utility and terminal windows |
| **Web & Info** | `wikipedia James Webb Telescope`, `who is Alan Turing` | Fetches concise 2-sentence Wikipedia summary |
| **Web & Info** | `play lofi beats on youtube`, `search youtube for python tutorials` | Launches YouTube media stream |
| **Web & Info** | `search google for quantum physics`, `google weather today` | Opens targeted Google search |
| **Live Data** | `what is the weather`, `current temperature`, `weather in Tokyo` | Reports hyper-local weather conditions |
| **Live Data** | `today's news`, `top headlines` | Reads top curated RSS news updates aloud |
| **Productivity** | `remember that meeting is at 4 PM`, `note down project deadline` | Stores timestamped entry to JSON memory |
| **Productivity** | `read notes`, `what did i ask you to remember`, `clear notes` | Reads recent entries or wipes scratchpad |
| **Dictionary** | `define serendipity`, `meaning of juxtapose` | Looks up word definition with fuzzy correction |
| **Persona** | `switch to friday`, `switch to jarvis`, `female voice`, `male voice` | Changes assistant voice and identity on the fly |
| **Utility** | `what time is it`, `today's date`, `my ip`, `tell me a joke` | Timestamp, local IP address, or programmer joke |
| **Exit** | `exit`, `quit`, `shutdown`, `goodbye`, `sleep` | Reports session duration and powers down |

---

## ⚙️ Configuration

Custom system settings are managed and validated automatically through `config.json`:

```json
{
    "user_name": "Vallu",
    "assistant_name": "JARVIS",
    "voice_gender": "male",
    "speech_rate": 180,
    "speech_volume": 1.0,
    "voice_enabled": true,
    "default_mode": "hybrid",
    "weather_city": "auto",
    "news_source": "google",
    "browser": "auto",
    "llm_enabled": true,
    "max_news_headlines": 4,
    "log_level": "INFO"
}
```

---

## 📊 Logging & Diagnostics

### Pre-Flight Self-Test
On startup, J.A.R.V.I.S executes a rapid self-test validating the operational status of all subsystems:

```
════════════════════════════════════════════════════════════════════════
                         J . A . R . V . I . S
                 Just A Rather Very Intelligent System
────────────────────────────────────────────────────────────────────────
  Version : 2.0 Pro          User    : Vallu
  Session : 05FE8538         Started : 2026-08-19  15:00:47
  Runtime : Python 3.13.5    Host    : VD
────────────────────────────────────────────────────────────────────────
[STARTUP SELF-TEST]
  [OK]  Voice Engine
  [OK]  Microphone
  [OK]  Weather Service
  [OK]  News Feed
  [OK]  Dictionary
  [OK]  Gemini AI Brain         Gemini API key found
  [OK]  Log System
────────────────────────────────────────────────────────────────────────
```

### Rotating File Logs
All commands, route resolutions, and error diagnostics are recorded in `logs/jarvis_YYYYMMDD.log`:

```log
[2026-08-19 15:00:47] [05FE8538] [INF] [jarvis:175] Session 05FE8538 started — mode=hybrid, user=Vallu
[2026-08-19 15:00:52] [05FE8538] [INF] [jarvis:135] Command matched → _cmd_sysinfo  query='cpu status'
[2026-08-19 15:01:05] [05FE8538] [INF] [ai_brain:75] GeminiBrain: Querying Gemini — 'explain quantum computing'
```

---

## 🗺️ Roadmap

- [x] Hybrid Voice + Console interaction engine
- [x] Configurable assistant personas (J.A.R.V.I.S / F.R.I.D.A.Y)
- [x] Priority Command Registry with 40+ intent handlers
- [x] Large Language Model integration with **Google Gemini 2.0 Flash**
- [x] Daily rotating session logger with UUID tracking
- [x] Timestamped JSON notes engine
- [ ] Offline Wake-Word Detection (e.g., OpenWakeWord / Porcupine)
- [ ] Smart Home / IoT Device Control via MQTT & Home Assistant
- [ ] Cross-Platform GUI Dashboard (Electron / PyQt6)

---

## 🤝 Contributing

Contributions make the open-source community an incredible place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. **Fork** the Project
2. **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the Branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

<div align="center">
  <sub>Built with ❤️ by passionate Python developers. Inspired by Marvel's J.A.R.V.I.S.</sub>
</div>
