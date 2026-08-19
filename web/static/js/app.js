/**
 * app.js — JARVIS Holographic HUD Client Controller
 * ===================================================
 * Lead Engineer: Production-Grade AI Assistant
 * Version: 2.0 Pro
 * Fully Responsive for Mobile, Tablet, Laptop, and Desktop
 */

(function () {
  'use strict';

  // ── State Management ───────────────────────────────────────────────────────
  const state = {
    connected: false,
    currentState: 'IDLE', // 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING'
    telemetry: {},
    voiceEnabled: true,
    speechRecognition: null,
    isRecording: false,
    ws: null,
    reconnectTimer: null,
    currentMobileTab: 'stage'
  };

  // ── DOM Element Selectors ──────────────────────────────────────────────────
  const dom = {
    // Top Bar
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    currentPersona: document.getElementById('currentPersona'),
    systemUptime: document.getElementById('systemUptime'),
    hudClock: document.getElementById('hudClock'),
    btnVoiceToggle: document.getElementById('btnVoiceToggle'),
    btnSettingsOpen: document.getElementById('btnSettingsOpen'),

    // Main Cockpit & Mobile Nav
    hudMain: document.querySelector('.hud-main'),
    mobileTabBtns: document.querySelectorAll('.mobile-tab-btn'),

    // Telemetry Left Wing
    cpuValue: document.getElementById('cpuValue'),
    cpuBar: document.getElementById('cpuBar'),
    ramValue: document.getElementById('ramValue'),
    ramBar: document.getElementById('ramBar'),
    ramDetails: document.getElementById('ramDetails'),
    diskValue: document.getElementById('diskValue'),
    diskBar: document.getElementById('diskBar'),
    diskDetails: document.getElementById('diskDetails'),
    batteryValue: document.getElementById('batteryValue'),
    batteryBar: document.getElementById('batteryBar'),
    batteryDetails: document.getElementById('batteryDetails'),
    networkIp: document.getElementById('networkIp'),
    brainLinkStatus: document.getElementById('brainLinkStatus'),

    // Center Stage
    reactorCanvas: document.getElementById('reactorCanvas'),
    reactorState: document.getElementById('reactorState'),
    reactorMode: document.getElementById('reactorMode'),
    waveVisualizer: document.getElementById('waveVisualizer'),
    chatStream: document.getElementById('chatStream'),
    cmdInput: document.getElementById('cmdInput'),
    btnMic: document.getElementById('btnMic'),
    btnSend: document.getElementById('btnSend'),
    quickChips: document.querySelectorAll('.chip-btn'),

    // Right Wing: Weather, News, Notes
    weatherCity: document.getElementById('weatherCity'),
    weatherTemp: document.getElementById('weatherTemp'),
    weatherCondition: document.getElementById('weatherCondition'),
    weatherWind: document.getElementById('weatherWind'),
    weatherHumidity: document.getElementById('weatherHumidity'),
    newsContainer: document.getElementById('newsContainer'),
    newsTabs: document.querySelectorAll('.news-tabs .tab-btn'),
    addNoteForm: document.getElementById('addNoteForm'),
    noteInput: document.getElementById('noteInput'),
    notesList: document.getElementById('notesList'),
    btnClearNotes: document.getElementById('btnClearNotes'),

    // Settings Modal
    settingsModal: document.getElementById('settingsModal'),
    btnSettingsClose: document.getElementById('btnSettingsClose'),
    btnSaveConfig: document.getElementById('btnSaveConfig'),
    cfgUserName: document.getElementById('cfgUserName'),
    cfgPersona: document.getElementById('cfgPersona'),
    cfgSpeechRate: document.getElementById('cfgSpeechRate'),
    speechRateVal: document.getElementById('speechRateVal'),
    cfgSpeechVolume: document.getElementById('cfgSpeechVolume'),
    speechVolumeVal: document.getElementById('speechVolumeVal'),
    cfgVoiceEnabled: document.getElementById('cfgVoiceEnabled')
  };

  // ── Clock Loop ─────────────────────────────────────────────────────────────
  function updateClock() {
    if (dom.hudClock) {
      const now = new Date();
      dom.hudClock.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
  }
  setInterval(updateClock, 1000);
  updateClock();

  // ── Mobile / Tablet Tab Switcher ───────────────────────────────────────────
  function switchMobileTab(target) {
    state.currentMobileTab = target;
    dom.mobileTabBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.target === target);
    });

    if (dom.hudMain) {
      dom.hudMain.className = `hud-main view-${target}`;
    }
  }

  dom.mobileTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      switchMobileTab(btn.dataset.target);
    });
  });

  // Default initial tab
  if (window.innerWidth <= 1023) {
    switchMobileTab('stage');
  }

  // ── Responsive Canvas Arc Reactor Visualizer ───────────────────────────────
  class ArcReactor {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.angle1 = 0;
      this.angle2 = 0;
      this.pulse = 0;
      this.pulseDir = 1;
      this.animId = null;
      this.resize();
      window.addEventListener('resize', () => this.resize());
      this.init();
    }

    resize() {
      const container = this.canvas.parentElement;
      if (!container) return;
      const rect = container.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const size = Math.floor(Math.min(rect.width, rect.height, 220)) || 140;

      this.canvas.width = size * dpr;
      this.canvas.height = size * dpr;
      this.canvas.style.width = `${size}px`;
      this.canvas.style.height = `${size}px`;
      
      // Reset transform before scaling to prevent cumulative scale drift
      this.ctx.setTransform(1, 0, 0, 1, 0, 0);
      this.ctx.scale(dpr, dpr);
      this.displaySize = size;
    }

    init() {
      const render = () => {
        this.draw();
        this.animId = requestAnimationFrame(render);
      };
      render();
    }

    draw() {
      const ctx = this.ctx;
      const size = this.displaySize || 140;
      const cx = size / 2;
      const cy = size / 2;

      ctx.clearRect(0, 0, size, size);

      let speed1 = 0.015;
      let speed2 = -0.02;
      let primaryColor = '#00f0ff';
      let glowColor = 'rgba(0, 240, 255, 0.5)';
      let pulseAmp = 2;

      if (state.currentState === 'LISTENING') {
        speed1 = 0.03;
        speed2 = -0.035;
        primaryColor = '#ff3366';
        glowColor = 'rgba(255, 51, 102, 0.6)';
        pulseAmp = 4;
      } else if (state.currentState === 'THINKING') {
        speed1 = 0.05;
        speed2 = -0.06;
        primaryColor = '#0077ff';
        glowColor = 'rgba(0, 119, 255, 0.7)';
        pulseAmp = 5;
      } else if (state.currentState === 'SPEAKING') {
        speed1 = 0.035;
        speed2 = -0.04;
        primaryColor = '#00ff9d';
        glowColor = 'rgba(0, 255, 157, 0.6)';
        pulseAmp = 6;
      }

      this.angle1 += speed1;
      this.angle2 += speed2;
      this.pulse += 0.05 * this.pulseDir;
      if (this.pulse > 1 || this.pulse < 0) this.pulseDir *= -1;

      const baseR = (size / 2) * 0.78;
      const dynamicRadius = baseR + this.pulse * pulseAmp;

      ctx.save();
      ctx.shadowBlur = 10;
      ctx.shadowColor = glowColor;

      // 1. Outer thin reference ring
      ctx.beginPath();
      ctx.arc(cx, cy, Math.max(10, dynamicRadius), 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.15)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      // 2. Outer Rotating Segments
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(this.angle1);
      ctx.beginPath();
      ctx.arc(0, 0, Math.max(12, dynamicRadius + (size * 0.04)), 0, Math.PI * 1.3);
      ctx.strokeStyle = primaryColor;
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(0, 0, Math.max(12, dynamicRadius + (size * 0.04)), Math.PI * 1.5, Math.PI * 1.9);
      ctx.strokeStyle = primaryColor;
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.restore();

      // 3. Middle Segmented Teeth Ring
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(this.angle2);
      const segments = 10;
      const midR = baseR * 0.72;
      for (let i = 0; i < segments; i++) {
        const theta = (i * 2 * Math.PI) / segments;
        ctx.beginPath();
        ctx.arc(0, 0, Math.max(8, midR), theta, theta + 0.35);
        ctx.strokeStyle = primaryColor;
        ctx.lineWidth = 2.5;
        ctx.stroke();
      }
      ctx.restore();

      // 4. Inner Reactor Core
      const coreR = Math.max(6, baseR * 0.5 + this.pulse * 1.5);
      ctx.beginPath();
      ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(10, 20, 45, 0.85)';
      ctx.fill();
      ctx.strokeStyle = primaryColor;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Core Tri-Nodes
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(-this.angle1 * 1.5);
      const nodeDist = coreR * 0.58;
      for (let i = 0; i < 3; i++) {
        const angle = (i * 2 * Math.PI) / 3;
        const nodeX = Math.cos(angle) * nodeDist;
        const nodeY = Math.sin(angle) * nodeDist;
        ctx.beginPath();
        ctx.arc(nodeX, nodeY, Math.max(1.5, size * 0.015), 0, Math.PI * 2);
        ctx.fillStyle = primaryColor;
        ctx.fill();
      }
      ctx.restore();

      // Center Core Dot
      ctx.beginPath();
      ctx.arc(cx, cy, Math.max(3, size * 0.035) + this.pulse * 1.2, 0, Math.PI * 2);
      ctx.fillStyle = primaryColor;
      ctx.shadowBlur = 8;
      ctx.shadowColor = primaryColor;
      ctx.fill();

      ctx.restore();
    }
  }

  const arcReactor = new ArcReactor(dom.reactorCanvas);

  // ── State Updates ──────────────────────────────────────────────────────────
  function setAssistantState(newState) {
    state.currentState = newState;
    if (dom.reactorState) dom.reactorState.textContent = newState;

    if (newState === 'SPEAKING' || newState === 'LISTENING') {
      if (dom.waveVisualizer) dom.waveVisualizer.classList.add('active');
    } else {
      if (dom.waveVisualizer) dom.waveVisualizer.classList.remove('active');
    }

    if (newState === 'LISTENING') {
      if (dom.btnMic) dom.btnMic.classList.add('recording');
      if (dom.statusDot) dom.statusDot.className = 'status-indicator busy';
      if (dom.statusText) dom.statusText.textContent = 'VOICE ACTIVE';
    } else {
      if (dom.btnMic) dom.btnMic.classList.remove('recording');
      if (dom.statusDot) dom.statusDot.className = 'status-indicator online';
      if (dom.statusText) dom.statusText.textContent = 'SYSTEM ONLINE';
    }
  }

  // ── WebSocket Connection Manager ───────────────────────────────────────────
  function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    state.ws = new WebSocket(wsUrl);

    state.ws.onopen = () => {
      state.connected = true;
      if (dom.statusDot) dom.statusDot.className = 'status-indicator online';
      if (dom.statusText) dom.statusText.textContent = 'SYSTEM ONLINE';
    };

    state.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleServerMessage(msg);
      } catch (err) {
        console.error('Error parsing WS message:', err);
      }
    };

    state.ws.onclose = () => {
      state.connected = false;
      if (dom.statusDot) dom.statusDot.className = 'status-indicator busy';
      if (dom.statusText) dom.statusText.textContent = 'RECONNECTING...';
      clearTimeout(state.reconnectTimer);
      state.reconnectTimer = setTimeout(initWebSocket, 2000);
    };

    state.ws.onerror = () => {
      if (state.ws) state.ws.close();
    };
  }

  function handleServerMessage(msg) {
    switch (msg.type) {
      case 'init':
        updateTelemetryUI(msg.telemetry);
        renderNotes(msg.notes || []);
        if (msg.telemetry && dom.currentPersona) {
          dom.currentPersona.textContent = msg.telemetry.persona || 'JARVIS';
        }
        break;

      case 'telemetry':
        updateTelemetryUI(msg.data);
        break;

      case 'state':
        setAssistantState(msg.state);
        break;

      case 'command_result':
        appendMessage('user', msg.query, 'COMMAND');
        appendMessage('assistant', msg.result.text, (msg.result.category || 'SYSTEM').toUpperCase());
        break;
    }
  }

  // ── Telemetry UI Updating ──────────────────────────────────────────────────
  function updateTelemetryUI(t) {
    if (!t) return;
    state.telemetry = t;

    // CPU
    if (dom.cpuValue) dom.cpuValue.textContent = `${t.cpu_percent}%`;
    if (dom.cpuBar) dom.cpuBar.style.width = `${Math.min(100, t.cpu_percent)}%`;

    // RAM
    if (dom.ramValue) dom.ramValue.textContent = `${t.ram_percent}%`;
    if (dom.ramBar) dom.ramBar.style.width = `${Math.min(100, t.ram_percent)}%`;
    if (dom.ramDetails) dom.ramDetails.textContent = `${t.ram_used_gb} / ${t.ram_total_gb} GB`;

    // Disk
    if (dom.diskValue) dom.diskValue.textContent = `${t.disk_percent}%`;
    if (dom.diskBar) dom.diskBar.style.width = `${Math.min(100, t.disk_percent)}%`;
    if (dom.diskDetails) dom.diskDetails.textContent = `${t.disk_free_gb} GB free`;

    // Battery
    if (dom.batteryValue) dom.batteryValue.textContent = `${t.battery_percent}%`;
    if (dom.batteryBar) dom.batteryBar.style.width = `${Math.min(100, t.battery_percent)}%`;
    if (dom.batteryDetails) dom.batteryDetails.textContent = t.battery_charging ? 'AC Connected' : 'Discharging';

    // Network & System Info
    if (dom.networkIp) dom.networkIp.textContent = t.ip_address || '127.0.0.1';
    if (dom.brainLinkStatus) dom.brainLinkStatus.textContent = t.brain_status || 'ONLINE';
    if (dom.systemUptime) dom.systemUptime.textContent = t.uptime || '00:00:00';
    if (dom.currentPersona) dom.currentPersona.textContent = t.persona || 'JARVIS';
  }

  // ── Chat Terminal Message Rendering ────────────────────────────────────────
  function appendMessage(role, text, category = 'SYSTEM') {
    if (!dom.chatStream) return;

    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${role}`;

    const authorName = role === 'user' ? (state.telemetry.user_name || 'Vallu') : (state.telemetry.assistant_name || 'J.A.R.V.I.S.');
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    bubble.innerHTML = `
      <div class="msg-meta">
        <span class="msg-author">${escapeHtml(authorName)}</span>
        <span class="msg-category">${escapeHtml(category)}</span>
        <span class="msg-time">${now}</span>
      </div>
      <div class="msg-content">${escapeHtml(text)}</div>
    `;

    dom.chatStream.appendChild(bubble);
    dom.chatStream.scrollTop = dom.chatStream.scrollHeight;

    // On mobile, if not on stage tab, switch back to stage to view response
    if (window.innerWidth <= 1023 && state.currentMobileTab !== 'stage') {
      switchMobileTab('stage');
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ── Command Dispatcher ─────────────────────────────────────────────────────
  async function sendCommand(query) {
    if (!query || !query.trim()) return;
    const cleanQuery = query.trim();
    if (dom.cmdInput) dom.cmdInput.value = '';

    setAssistantState('THINKING');

    if (state.ws && state.connected) {
      state.ws.send(JSON.stringify({
        type: 'command',
        query: cleanQuery,
        speak: state.voiceEnabled
      }));
    } else {
      try {
        const resp = await fetch('/api/command', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: cleanQuery, speak: state.voiceEnabled })
        });
        const data = await resp.json();
        appendMessage('user', cleanQuery, 'COMMAND');
        appendMessage('assistant', data.result.text, (data.result.category || 'SYSTEM').toUpperCase());
        setAssistantState('IDLE');
      } catch (err) {
        console.error('Command API error:', err);
        appendMessage('assistant', 'Communication link failure, Sir.', 'ERROR');
        setAssistantState('IDLE');
      }
    }
  }

  // ── Web Speech API (In-Browser Microphone) ──────────────────────────────────
  function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      if (dom.btnMic) dom.btnMic.title = 'Voice input not supported in this browser';
      return;
    }

    const recognizer = new SpeechRecognition();
    recognizer.continuous = false;
    recognizer.interimResults = true;
    recognizer.lang = 'en-US';

    recognizer.onstart = () => {
      state.isRecording = true;
      setAssistantState('LISTENING');
      if (dom.cmdInput) dom.cmdInput.placeholder = 'Listening... Speak clearly...';
    };

    recognizer.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      if (dom.cmdInput) dom.cmdInput.value = transcript;
    };

    recognizer.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      state.isRecording = false;
      setAssistantState('IDLE');
      if (dom.cmdInput) dom.cmdInput.placeholder = 'Give JARVIS a command...';
    };

    recognizer.onend = () => {
      state.isRecording = false;
      setAssistantState('IDLE');
      if (dom.cmdInput) dom.cmdInput.placeholder = 'Give JARVIS a command...';
      const speechQuery = dom.cmdInput ? dom.cmdInput.value.trim() : '';
      if (speechQuery) {
        sendCommand(speechQuery);
      }
    };

    state.speechRecognition = recognizer;
  }

  function toggleVoiceInput() {
    if (!state.speechRecognition) {
      alert('Voice Recognition requires Google Chrome, Microsoft Edge, or Apple Safari.');
      return;
    }

    if (state.isRecording) {
      state.speechRecognition.stop();
    } else {
      state.speechRecognition.start();
    }
  }

  // ── Quick Launcher Grid Actions ────────────────────────────────────────────
  document.querySelectorAll('.launch-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const action = btn.dataset.action;
      const target = btn.dataset.target;

      try {
        const resp = await fetch('/api/system/control', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: action === 'launch' ? 'launch' : action, target: target })
        });
        const res = await resp.json();
        appendMessage('assistant', res.message, 'LAUNCHER');
      } catch (err) {
        console.error('System action failed:', err);
      }
    });
  });

  // ── Weather Loader ─────────────────────────────────────────────────────────
  async function loadWeather() {
    try {
      const resp = await fetch('/api/weather');
      const data = await resp.json();
      if (data.success) {
        if (dom.weatherCity) dom.weatherCity.textContent = data.city || 'LOCAL';
        if (dom.weatherTemp) dom.weatherTemp.textContent = `${data.temperature}°C`;
        if (dom.weatherCondition) dom.weatherCondition.textContent = data.condition || 'Clear';
        if (dom.weatherWind) dom.weatherWind.textContent = `Wind: ${data.wind_speed || 0} km/h`;
        if (dom.weatherHumidity) dom.weatherHumidity.textContent = `${data.humidity || 0}%`;
      }
    } catch (err) {
      console.warn('Failed to load weather:', err);
    }
  }

  // ── News Feed Loader ───────────────────────────────────────────────────────
  async function loadNews(category = 'top') {
    if (!dom.newsContainer) return;
    dom.newsContainer.innerHTML = '<div class="loading-spinner">Loading intelligence feed...</div>';
    try {
      const resp = await fetch(`/api/news?category=${category}&limit=5`);
      const data = await resp.json();
      if (data.articles && data.articles.length > 0) {
        dom.newsContainer.innerHTML = data.articles.map(art => `
          <a href="${escapeHtml(art.link)}" target="_blank" rel="noopener noreferrer" class="news-item">
            <span class="news-title">${escapeHtml(art.title)}</span>
          </a>
        `).join('');
      } else {
        dom.newsContainer.innerHTML = '<div class="empty-state">No news stories found.</div>';
      }
    } catch (err) {
      dom.newsContainer.innerHTML = '<div class="empty-state">Unable to load news feed.</div>';
    }
  }

  dom.newsTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      dom.newsTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      loadNews(tab.dataset.cat);
    });
  });

  // ── Memory Notes Manager ───────────────────────────────────────────────────
  function renderNotes(notes) {
    if (!dom.notesList) return;
    if (!notes || notes.length === 0) {
      dom.notesList.innerHTML = '<div class="empty-state">No memory records saved.</div>';
      return;
    }

    dom.notesList.innerHTML = notes.map(note => `
      <div class="note-item" data-id="${note.id}">
        <div class="note-info">
          <span class="note-text">${escapeHtml(note.text)}</span>
          <span class="note-date">${escapeHtml(note.timestamp || '')}</span>
        </div>
        <button class="note-del-btn" onclick="window.jarvisDeleteNote(${note.id})" title="Delete note" aria-label="Delete Note">&times;</button>
      </div>
    `).join('');
  }

  window.jarvisDeleteNote = async function (noteId) {
    try {
      await fetch(`/api/notes/${noteId}`, { method: 'DELETE' });
      const resp = await fetch('/api/notes');
      const notes = await resp.json();
      renderNotes(notes);
    } catch (err) {
      console.error('Delete note failed:', err);
    }
  };

  if (dom.addNoteForm) {
    dom.addNoteForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = dom.noteInput ? dom.noteInput.value.trim() : '';
      if (!text) return;
      try {
        await fetch('/api/notes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: text, category: 'general' })
        });
        if (dom.noteInput) dom.noteInput.value = '';
        const resp = await fetch('/api/notes');
        const notes = await resp.json();
        renderNotes(notes);
      } catch (err) {
        console.error('Add note failed:', err);
      }
    });
  }

  if (dom.btnClearNotes) {
    dom.btnClearNotes.addEventListener('click', async () => {
      if (confirm('Clear all stored memory notes, Sir?')) {
        await fetch('/api/notes/clear', { method: 'POST' });
        renderNotes([]);
      }
    });
  }

  // ── Settings Modal ─────────────────────────────────────────────────────────
  if (dom.btnSettingsOpen) {
    dom.btnSettingsOpen.addEventListener('click', async () => {
      try {
        const resp = await fetch('/api/config');
        const cfg = await resp.json();
        if (dom.cfgUserName) dom.cfgUserName.value = cfg.user_name || 'Vallu';
        if (dom.cfgPersona) dom.cfgPersona.value = cfg.assistant_name || 'JARVIS';
        if (dom.cfgSpeechRate) {
          dom.cfgSpeechRate.value = cfg.speech_rate || 180;
          if (dom.speechRateVal) dom.speechRateVal.textContent = cfg.speech_rate || 180;
        }
        if (dom.cfgSpeechVolume) {
          dom.cfgSpeechVolume.value = cfg.speech_volume || 1.0;
          if (dom.speechVolumeVal) dom.speechVolumeVal.textContent = Math.round((cfg.speech_volume || 1.0) * 100);
        }
        if (dom.cfgVoiceEnabled) dom.cfgVoiceEnabled.checked = cfg.voice_enabled !== false;
        if (dom.settingsModal) dom.settingsModal.classList.add('open');
      } catch (err) {
        console.error('Failed to load settings:', err);
      }
    });
  }

  if (dom.btnSettingsClose) {
    dom.btnSettingsClose.addEventListener('click', () => {
      if (dom.settingsModal) dom.settingsModal.classList.remove('open');
    });
  }

  if (dom.cfgSpeechRate) {
    dom.cfgSpeechRate.addEventListener('input', (e) => {
      if (dom.speechRateVal) dom.speechRateVal.textContent = e.target.value;
    });
  }

  if (dom.cfgSpeechVolume) {
    dom.cfgSpeechVolume.addEventListener('input', (e) => {
      if (dom.speechVolumeVal) dom.speechVolumeVal.textContent = Math.round(e.target.value * 100);
    });
  }

  if (dom.btnSaveConfig) {
    dom.btnSaveConfig.addEventListener('click', async () => {
      try {
        await fetch('/api/config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_name: dom.cfgUserName ? dom.cfgUserName.value.trim() : 'Vallu',
            persona: dom.cfgPersona ? dom.cfgPersona.value : 'JARVIS',
            speech_rate: dom.cfgSpeechRate ? parseInt(dom.cfgSpeechRate.value) : 180,
            speech_volume: dom.cfgSpeechVolume ? parseFloat(dom.cfgSpeechVolume.value) : 1.0,
            voice_enabled: dom.cfgVoiceEnabled ? dom.cfgVoiceEnabled.checked : true
          })
        });
        if (dom.settingsModal) dom.settingsModal.classList.remove('open');
        if (dom.currentPersona && dom.cfgPersona) dom.currentPersona.textContent = dom.cfgPersona.value;
        appendMessage('assistant', 'Configuration protocols successfully updated, Sir.', 'CONFIG');
      } catch (err) {
        console.error('Failed to save config:', err);
      }
    });
  }

  // ── Voice Mute Quick Toggle ────────────────────────────────────────────────
  if (dom.btnVoiceToggle) {
    dom.btnVoiceToggle.addEventListener('click', () => {
      state.voiceEnabled = !state.voiceEnabled;
      dom.btnVoiceToggle.style.color = state.voiceEnabled ? 'var(--cyan-core)' : 'var(--text-muted)';
      fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice_enabled: state.voiceEnabled })
      });
    });
  }

  // ── Input & Chip Event Listeners ───────────────────────────────────────────
  if (dom.btnSend) {
    dom.btnSend.addEventListener('click', () => {
      if (dom.cmdInput) sendCommand(dom.cmdInput.value);
    });
  }

  if (dom.cmdInput) {
    dom.cmdInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        sendCommand(dom.cmdInput.value);
      }
    });
  }

  if (dom.btnMic) {
    dom.btnMic.addEventListener('click', toggleVoiceInput);
  }

  dom.quickChips.forEach(chip => {
    chip.addEventListener('click', () => {
      sendCommand(chip.dataset.query);
    });
  });

  // ── App Initialization ─────────────────────────────────────────────────────
  initWebSocket();
  initSpeechRecognition();
  loadWeather();
  loadNews('top');

})();
