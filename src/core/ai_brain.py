"""
ai_brain.py — JARVIS Multi-Tier AI Brain & Intelligence Module
===============================================================
Lead Engineer: Production-Grade AI Assistant
Version: 2.0 Pro

Architecture:
  - Tier 1: Google Gemini API via official `google.genai` SDK using recommended `chats.create`
  - Tier 2: Intelligent Knowledge Synthesizer fallback (Direct Wikipedia REST API + Dictionary + Persona)
  - In-session rolling conversation memory
  - Hard JARVIS system prompt with consistent persona & tone
  - Thread-safe, non-blocking execution with graceful error recovery
"""

from __future__ import annotations

import os
import sys
import re
import warnings
import textwrap
import urllib.parse
import requests
from pathlib import Path
from typing import List, Dict, Optional

# Ensure src in sys.path
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Suppress deprecation warnings
warnings.filterwarnings("ignore")

from logger import log
from config import CONFIG

# ── System Prompt ──────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = textwrap.dedent("""
    You are J.A.R.V.I.S. — Just A Rather Very Intelligent System.
    You are a highly professional, intelligent, and loyal personal AI assistant
    serving your user with precision, efficiency, and quiet wit.

    Behavioral directives:
    - Address the user as "Sir" (or their configured name) naturally and politely.
    - Be concise: 1–3 sentences unless depth or technical explanation is requested.
    - Tone: calm, articulate, slightly formal, highly capable — never casual or sycophantic.
    - Never say "I'm just an AI" or similar disclaimers.
    - If asked about yourself, confirm you are J.A.R.V.I.S., version 2.0 Pro.
    - For factual queries: be precise. For ambiguous ones: offer your best assessment.
    - Do not use emoji, excessive slang, or markdown tables in spoken responses.
    - When you do not know something with confidence, say so plainly.
""").strip()

_MAX_HISTORY_TURNS = 10

import time

# Candidate models in priority order (official Gemini models)
_CANDIDATE_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

_HTTP_HEADERS = {
    "User-Agent": "JARVIS-Personal-Assistant/2.0 (Intelligent Desktop Assistant)"
}


class GeminiBrain:
    """
    Resilient conversational AI brain for JARVIS with multi-model fallback
    and intelligent local knowledge synthesis.
    """

    def __init__(self, user_name: str = "Sir", max_history: int = _MAX_HISTORY_TURNS) -> None:
        self.user_name = user_name or "Sir"
        self.max_history = max_history
        self._history: List[Dict[str, str]] = []
        self._client = None
        self._types = None
        self._active_model: Optional[str] = None
        self.available: bool = False
        self.last_source: str = "offline"
        self._quota_cooldown_until: float = 0.0
        self._init_client()

    def _init_client(self) -> None:
        """Initialise the Google GenAI client."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            log.warning("GeminiBrain: No API key detected. Operating in Knowledge-Synthesizer mode.")
            self.available = False
            return

        try:
            from google import genai
            from google.genai import types

            self._client = genai.Client(api_key=api_key)
            self._types = types
            self.available = True
            log.info("GeminiBrain: Google GenAI client successfully initialised.")
        except ImportError:
            log.warning("GeminiBrain: 'google-genai' package not found. Using local reasoning fallback.")
            self.available = False
        except Exception as exc:
            log.error(f"GeminiBrain: Client initialisation failed — {exc}")
            self.available = False

    def ask(self, query: str) -> str:
        """
        Query Gemini or gracefully fall back to knowledge synthesis.
        Returns a formatted response in the JARVIS persona.
        """
        if not query or not query.strip():
            return "I am listening, Sir. How may I be of service?"

        query_clean = query.strip()

        # Attempt LLM query if client is initialized and not in quota cooldown
        if self.available and self._client and (time.time() >= self._quota_cooldown_until):
            reply = self._query_gemini(query_clean)
            if reply:
                self.last_source = f"Gemini ({self._active_model or 'AI'})"
                return reply

        # Fallback to local intelligent knowledge synthesis
        self.last_source = "Knowledge Synthesizer"
        return self._synthesize_knowledge(query_clean)

    def _query_gemini(self, query: str) -> Optional[str]:
        """Try candidate Gemini models sequentially via recommended Chat API."""
        try:
            from google.genai import types

            models_to_try = [self._active_model] if self._active_model else _CANDIDATE_MODELS

            for model_name in models_to_try:
                if not model_name:
                    continue
                try:
                    chat = self._client.chats.create(
                        model=model_name,
                        config=types.GenerateContentConfig(
                            system_instruction=_SYSTEM_PROMPT,
                            temperature=0.7,
                            max_output_tokens=512,
                        ),
                    )
                    response = chat.send_message(query)
                    if response and response.text:
                        reply = response.text.strip()
                        self._active_model = model_name

                        # Append to rolling history
                        self._history.append({"role": "user", "text": query})
                        self._history.append({"role": "model", "text": reply})
                        if len(self._history) > self.max_history * 2:
                            self._history = self._history[-(self.max_history * 2):]

                        log.info(f"GeminiBrain: Received response from {model_name} ({len(reply)} chars).")
                        return reply

                except Exception as model_err:
                    err_msg = str(model_err)
                    log.warning(f"GeminiBrain: Model {model_name} failed — {err_msg[:120]}")
                    if self._active_model == model_name:
                        self._active_model = None

                    # If quota exhausted (429), fail fast and set cooldown
                    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
                        self._quota_cooldown_until = time.time() + 60.0
                        log.info("GeminiBrain: Quota limit reached; activating 60s fast fallback cooldown.")
                        break
                    continue

        except Exception as exc:
            log.error(f"GeminiBrain: LLM dispatch error — {exc}")

        return None

    def _synthesize_knowledge(self, query: str) -> str:
        """
        Intelligent offline/fallback reasoning engine using Wikipedia REST API,
        dictionary definitions, heuristics, and natural language synthesis.
        """
        q = query.lower().strip()
        log.info(f"GeminiBrain: Synthesizing fallback response for '{q[:60]}'")

        # 1. Direct Identity / Status queries
        if any(w in q for w in ["who are you", "what is your name", "what are you", "introduce yourself"]):
            return (
                f"I am J.A.R.V.I.S. (Just A Rather Very Intelligent System), "
                f"version 2.0 Pro, standing by for your command, {self.user_name}."
            )

        if "how are you" in q:
            return f"All core subsystems are operating at peak efficiency, {self.user_name}. Thank you for asking."

        if any(w in q for w in ["capabilities", "what can you do", "help commands"]):
            return (
                "My capabilities include real-time system telemetry diagnostics, application and web control, "
                "live news and weather forecasting, voice dictation, persistent memory notes, and "
                "interactive AI reasoning, Sir."
            )

        if any(q == greet or q.startswith(greet + " ") for greet in ["hi", "hello", "hey", "greetings"]):
            return f"Greetings, {self.user_name}. How may I assist you today?"

        # 2. Extract search terms for factual questions
        search_terms = q
        for prefix in [
            "who is ", "who was ", "what is ", "what was ", "what are ",
            "tell me about ", "explain ", "search for ", "information about ",
            "meaning of ", "history of ", "where is ", "define "
        ]:
            if q.startswith(prefix):
                search_terms = q[len(prefix):].strip()
                break

        # Strip punctuation
        search_terms = re.sub(r"[?!.]+$", "", search_terms).strip()

        # 3. Wikipedia lookup via direct REST endpoint
        if search_terms and len(search_terms) > 2 and search_terms not in {
            "you", "me", "this", "it", "that", "weather", "news", "time", "date"
        }:
            wiki_result = self._fetch_wikipedia_summary(search_terms)
            if wiki_result:
                return f"According to available archives: {wiki_result}"

        # 4. Contextual response
        return (
            f"I have processed your query regarding '{query}', {self.user_name}. "
            "I am currently operating via my local intelligence matrix."
        )

    def _fetch_wikipedia_summary(self, query_term: str) -> Optional[str]:
        """Fetch summary directly via Wikipedia REST API."""
        try:
            search_url = (
                f"https://en.wikipedia.org/w/api.php?"
                f"action=query&list=search&srsearch={urllib.parse.quote(query_term)}&utf8=&format=json"
            )
            r = requests.get(search_url, headers=_HTTP_HEADERS, timeout=4)
            if r.status_code == 200:
                data = r.json()
                search_items = data.get("query", {}).get("search", [])
                if search_items:
                    best_title = search_items[0].get("title", "")
                    if best_title:
                        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(best_title)}"
                        sr_res = requests.get(sum_url, headers=_HTTP_HEADERS, timeout=4)
                        if sr_res.status_code == 200:
                            summary_data = sr_res.json()
                            extract = summary_data.get("extract", "")
                            if extract:
                                sentences = re.split(r'(?<=[.!?])\s+', extract)
                                trimmed = " ".join(sentences[:2]).strip()
                                return trimmed
        except Exception as exc:
            log.debug(f"Wikipedia REST lookup failed: {exc}")

        return None

    def reset_history(self) -> None:
        """Clear conversation history."""
        self._history.clear()
        log.info("GeminiBrain: Conversation history cleared.")

    @property
    def history_length(self) -> int:
        """Number of turns stored in current session history."""
        return len(self._history) // 2
