<div align="center">

# 🤖 J.A.R.V.I.S — Desktop AI Assistant

**Just A Rather Very Intelligent System — A Modular, Multi-Modal Python Voice & Automation Assistant**

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform Support](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/bunnyvalluri/J.A.R.V.I.S)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](#)

<br/>

<img src="jarvis1.jpg" alt="JARVIS Banner" width="800" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);"/>

<br/>

<p align="center">
  <a href="#-key-features">Key Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-command-reference">Command Reference</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-media-showcase">Showcase</a> •
  <a href="#-contributing">Contributing</a>
</p>

</div>

---

## 🌟 Overview

**J.A.R.V.I.S** is a comprehensive, production-grade desktop virtual assistant crafted in Python. Designed for productivity, automation, and convenience, it bridges offline voice synthesis with real-time web services, computer vision security, system telemetry, and desktop application orchestration.

Whether you prefer natural hands-free voice commands or rapid keyboard input in the interactive terminal, J.A.R.V.I.S seamlessly adapts to your workflow.

---

## ✨ Key Features

<table>
  <tr>
    <td width="50%">
      <h3>🎙️ Multi-Modal Interaction</h3>
      <ul>
        <li><b>Hybrid Input:</b> Seamlessly accept mic voice or console typing.</li>
        <li><b>Voice Persona Switcher:</b> Switch on-the-fly between <b>J.A.R.V.I.S</b> (Male) and <b>F.R.I.D.A.Y</b> (Female).</li>
        <li><b>Offline Speech Synthesis:</b> Fast, low-latency text-to-speech via <code>pyttsx3</code>.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>⚡ System Control & Telemetry</h3>
      <ul>
        <li><b>Hardware Diagnostics:</b> Real-time CPU usage, RAM utilization, and battery status.</li>
        <li><b>Automated Screenshots:</b> Instant capture saved automatically to your Pictures directory.</li>
        <li><b>OS Operations:</b> Volume adjustment, workstation lock, IP lookup, date/time queries.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🚀 App Launcher & Automation</h3>
      <ul>
        <li><b>Developer & Productivity Tools:</b> One-click launch for VS Code, Terminal, WhatsApp, Notepad, Task Manager, and Calculator.</li>
        <li><b>Media Control:</b> Direct integration with Spotify and web media streams.</li>
        <li><b>Deep Search:</b> Direct query routing for Google, YouTube, and Wikipedia summaries.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🌐 Intelligence & Utilities</h3>
      <ul>
        <li><b>Live Weather & Geolocation:</b> Dynamic temperature, humidity, wind, and forecast metrics.</li>
        <li><b>Real-Time News:</b> Multi-source headline feeds (Google News, BBC, Times of India).</li>
        <li><b>Intelligent Dictionary:</b> Built-in definition lookup with typo auto-correction & fuzzy matching.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>📝 Productivity & Notes</h3>
      <ul>
        <li><b>Persistent Scratchpad:</b> Quick dictation, storage, retrieval, and clearing of notes/todos.</li>
        <li><b>Multi-Language Translation:</b> Translation assistance for phrases and terminology.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>👁️ Vision & Media Tools</h3>
      <ul>
        <li><b>Face Recognition Auth:</b> Integrated OpenCV facial authentication pipeline.</li>
        <li><b>Media Downloader:</b> Standalone YouTube video downloading module.</li>
        <li><b>Optical Character Recognition (OCR):</b> Text extraction from image inputs.</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🏛️ Architecture

```
J.A.R.V.I.S/
├── jarvis.py                 # Core application controller & intent router
├── config.py                 # Central configuration manager (config.json)
├── voice_engine.py           # Text-to-speech engine & persona management
├── helpers.py                # Command listener, speech recognition & utilities
├── system_control.py         # Hardware telemetry, volume & OS-level commands
├── app_launcher.py           # Desktop app & web navigation launcher
├── weather_service.py        # Geolocation & weather forecasting service
├── news.py                   # News API aggregator and narrator
├── diction.py                # Intelligent dictionary & fuzzy search
├── OCR.py                    # Optical Character Recognition module
├── youtube_downloader.py     # YouTube media fetcher
├── ui.py                     # Rich terminal styling & visual diagnostics
├── Face-Recognition/         # Computer vision authentication module
├── requirements.txt          # Python dependencies
└── config.json               # User preferences & environment configuration
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python:** 3.8, 3.9, 3.10, or 3.11 recommended.
- **Microphone & Speaker:** Standard audio I/O devices.
- **Git:** Version control installed.

### 2. Installation

Clone the repository and set up a virtual environment:

```bash
# Clone the repository
git clone https://github.com/bunnyvalluri/J.A.R.V.I.S.git
cd J.A.R.V.I.S

# Create and activate virtual environment
# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS / Linux:
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

> [!TIP]
> **Windows Audio Setup:** If you encounter issues installing `PyAudio`, use the included wheel file or install via `pipwin`:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```
> **Linux (Ubuntu/Debian) Users:** Ensure system audio libraries and speech tools are installed:
> ```bash
> sudo apt-get update && sudo apt-get install espeak portaudio19-dev libasound-dev
> ```

---

## 🎮 Execution Modes

Run J.A.R.V.I.S in your preferred operational mode:

```bash
# 1. Standard Interactive Mode (Mic Voice + Fast Terminal Input)
python jarvis.py

# 2. Text-Only Mode (Console input only, no microphone listening)
python jarvis.py --text

# 3. Voice-Only Mode (Hands-free voice recognition)
python jarvis.py --voice

# 4. Persona Selection
python jarvis.py --friday   # Starts with female assistant persona
python jarvis.py --jarvis   # Starts with male assistant persona
```

---

## 📖 Command Reference

J.A.R.V.I.S understands natural queries. Here are some of the most common commands:

| Category | Example Voice / Typed Commands | Action Performed |
| :--- | :--- | :--- |
| **System** | `cpu status`, `system stats`, `battery` | Reports CPU, Memory, and Battery health |
| **System** | `take screenshot`, `capture screen` | Saves full screenshot to `Pictures/JARVIS_Screenshots` |
| **System** | `volume up`, `volume down`, `mute` | Adjusts master system audio |
| **System** | `lock screen`, `lock workstation` | Secures the operating system session |
| **Apps** | `open vscode`, `open code` | Launches Visual Studio Code workspace |
| **Apps** | `open whatsapp`, `open spotify` | Opens designated desktop/web application |
| **Apps** | `open calculator`, `open notepad` | Opens native Windows utility tools |
| **Web & Info** | `wikipedia Albert Einstein` | Retrieves concise Wikipedia summary |
| **Web & Info** | `search youtube lofi music` | Searches and launches YouTube query |
| **Web & Info** | `weather in London`, `current weather` | Fetches live weather conditions |
| **Web & Info** | `latest news`, `news headlines` | Reads top news updates aloud |
| **Productivity** | `take a note`, `write note <content>` | Stores note into local scratchpad |
| **Productivity** | `read notes`, `clear notes` | Reads saved notes or wipes history |
| **Dictionary** | `define serendipity`, `meaning of quantum` | Looks up definitions with fuzzy correction |
| **Persona** | `switch to friday`, `switch to jarvis` | Changes assistant voice and identity |
| **General** | `tell me a joke`, `what time is it` | Reads humorous programmer joke or timestamp |
| **Exit** | `exit`, `quit`, `goodbye`, `shutdown` | Powers down the assistant safely |

---

## ⚙️ Configuration

Custom settings can be modified anytime in `config.json`:

```json
{
    "user_name": "Sir",
    "assistant_name": "JARVIS",
    "voice_gender": "male",
    "speech_rate": 180,
    "speech_volume": 1.0,
    "voice_enabled": true,
    "default_mode": "hybrid",
    "weather_city": "auto",
    "news_source": "google",
    "browser": "auto"
}
```

---

## 📸 Media & Showcase

<div align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <img src="images/Screenshot%20(138).png" alt="Console Interface" width="100%"/>
        <br/><b>Interactive Diagnostic Terminal</b>
      </td>
      <td align="center" width="50%">
        <img src="images/face-600x900.png" alt="Face Recognition" width="100%"/>
        <br/><b>Computer Vision & Facial Recognition</b>
      </td>
    </tr>
    <tr>
      <td align="center" width="50%">
        <img src="images/email.jpg" alt="Email Automation" width="100%"/>
        <br/><b>Automated Email Pipeline</b>
      </td>
      <td align="center" width="50%">
        <img src="canny.jpg" alt="Image Processing" width="100%"/>
        <br/><b>Image Processing & Edge Detection</b>
      </td>
    </tr>
  </table>
</div>

---

## 🗺️ Roadmap & Upcoming Features

- [x] Hybrid Voice + Console interaction engine
- [x] Configurable assistant personas (J.A.R.V.I.S / F.R.I.D.A.Y)
- [x] Comprehensive system diagnostic dashboard
- [ ] Large Language Model (LLM) Integration (OpenAI / Gemini / Ollama)
- [ ] Offline Wake-Word Detection (e.g. Porcupine / Snowboy)
- [ ] Smart Home / IoT Device Control via MQTT & Home Assistant
- [ ] Cross-platform GUI Dashboard (PyQt6 / Electron)

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
