# 🔌 J.A.R.V.I.S. API Reference

The JARVIS Web Backend provides both a REST API suite and a bidirectional real-time WebSocket protocol.

Base URL: `http://localhost:8000`

---

## 🌐 WebSocket Protocol (`/ws`)

### Connection:
`ws://localhost:8000/ws`

### Server &rarr; Client Messages:

#### 1. Initial State (`init`):
```json
{
  "type": "init",
  "telemetry": { ... },
  "notes": [ ... ],
  "history": [ ... ]
}
```

#### 2. Periodic Telemetry Broadcast (`telemetry`):
Sent automatically every 1.5 seconds to all connected clients:
```json
{
  "type": "telemetry",
  "data": {
    "version": "2.0 Pro",
    "assistant_name": "JARVIS",
    "persona": "JARVIS",
    "cpu_percent": 14.2,
    "ram_percent": 62.8,
    "ram_used_gb": 9.8,
    "ram_total_gb": 15.7,
    "disk_percent": 80.9,
    "disk_free_gb": 91.0,
    "battery_percent": 85,
    "battery_charging": true,
    "ip_address": "192.168.1.2",
    "uptime": "1 day, 08:35:12",
    "brain_status": "ONLINE"
  }
}
```

#### 3. Command Execution Result (`command_result`):
```json
{
  "type": "command_result",
  "query": "what is the time",
  "result": {
    "success": true,
    "text": "Sir, it is currently 03:35 PM on Wednesday, August 19, 2026.",
    "spoken": "Sir, it is currently 03:35 PM on Wednesday, August 19, 2026.",
    "category": "clock",
    "data": null,
    "should_exit": false
  }
}
```

### Client &rarr; Server Messages:

#### 1. Send Command:
```json
{
  "type": "command",
  "query": "open spotify",
  "speak": true
}
```

---

## 📡 REST API Endpoints

### 1. System Telemetry
- **Endpoint**: `GET /api/status`
- **Response**:
```json
{
  "status": "online",
  "telemetry": {
    "cpu_percent": 12.5,
    "ram_percent": 60.1,
    "battery_percent": 100,
    ...
  }
}
```

### 2. Execute Command
- **Endpoint**: `POST /api/command`
- **Request Body**:
```json
{
  "query": "search youtube for Hans Zimmer",
  "speak": true
}
```
- **Response**:
```json
{
  "query": "search youtube for Hans Zimmer",
  "result": {
    "success": true,
    "text": "Searching YouTube for 'Hans Zimmer', Sir.",
    "spoken": "Searching YouTube for 'Hans Zimmer', Sir.",
    "category": "media"
  }
}
```

### 3. Memory Notes Vault
- `GET /api/notes`: Returns array of saved notes.
- `POST /api/notes`:
```json
{
  "text": "Call product team at 5 PM",
  "category": "work"
}
```
- `DELETE /api/notes/{id}`: Deletes note by integer ID.
- `POST /api/notes/clear`: Wipes all notes.

### 4. Weather & Atmosphere
- `GET /api/weather`
- **Response**:
```json
{
  "success": true,
  "city": "Hyderabad",
  "temperature": 30.2,
  "condition": "Partly cloudy",
  "humidity": 58,
  "wind_speed": 18.0,
  "spoken": "In Hyderabad, the weather is currently partly cloudy with a temperature of 30.2°C...",
  "display": "Partly cloudy | 30.2°C | Humidity: 58% | Wind: 18.0 km/h (Hyderabad)"
}
```

### 5. News Headlines
- `GET /api/news?category=top&limit=5`
- Categories supported: `top`, `tech`, `world`, `india`.

### 6. Hardware & System Actions
- `POST /api/system/control`
- **Request Body**:
```json
{
  "action": "screenshot"
}
```
*Supported actions:* `screenshot`, `lock`, `volume_up`, `volume_down`, `volume_mute`, `launch` (with `target`).

### 7. Configuration Protocols
- `GET /api/config`: Returns active assistant configuration.
- `POST /api/config`:
```json
{
  "user_name": "Vallu",
  "persona": "FRIDAY",
  "speech_rate": 190,
  "speech_volume": 1.0,
  "voice_enabled": true
}
```
