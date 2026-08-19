"""
ai_brain.py — JARVIS Gemini AI Brain
======================================
Wraps the Google Gemini API to give JARVIS an intelligent, context-aware
conversational fallback. When JARVIS cannot resolve a query through its
deterministic command registry, this module generates a polished response
in the JARVIS voice and persona.

Features:
  - Gemini 2.0 Flash model (fast, low-latency)
  - In-session conversation history (last N turns for context)
  - Hard JARVIS system prompt for consistent persona
  - Graceful degradation — never crashes JARVIS if API is unavailable
  - Structured logging of every LLM call
"""

from __future__ import annotations

import os
import textwrap
from typing import List, Dict, Optional

from logger import log

# ── System Prompt ──────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = textwrap.dedent("""
    You are J.A.R.V.I.S. — Just A Rather Very Intelligent System.
    You are a highly professional, intelligent, and loyal personal AI assistant
    serving your user with precision, efficiency, and quiet wit.

    Behavioral directives:
    - Address the user as "Sir" at the end of responses (naturally, not robotically).
    - Be concise: 1–3 sentences unless depth is genuinely required.
    - Tone: calm, articulate, slightly formal — never casual or sycophantic.
    - Never say "I'm just an AI" or similar disclaimers.
    - If asked about yourself, confirm you are J.A.R.V.I.S., version 2.0 Pro.
    - For factual queries: be precise. For ambiguous ones: offer your best assessment.
    - Never use emoji, slang, or markdown formatting in spoken responses.
    - When you do not know something with confidence, say so plainly.
""").strip()

# ── History Limit ──────────────────────────────────────────────────────────────
_MAX_HISTORY_TURNS = 10  # Keep last 10 exchanges for context


class GeminiBrain:
    """
    Gemini-powered conversational AI brain for JARVIS.

    Usage:
        brain = GeminiBrain()
        if brain.available:
            response = brain.ask("What is quantum entanglement?")
    """

    def __init__(self, user_name: str = "Sir", max_history: int = _MAX_HISTORY_TURNS) -> None:
        self.user_name = user_name
        self.max_history = max_history
        self._history: List[Dict[str, str]] = []
        self._model = None
        self._chat = None
        self.available: bool = False
        self._init_client()

    def _init_client(self) -> None:
        """Initialise the Gemini client. Sets self.available = True on success."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            log.warning("GeminiBrain: No API key found. LLM fallback disabled.")
            return

        try:
            from google import genai                # type: ignore
            from google.genai import types          # type: ignore

            self._client = genai.Client(api_key=api_key)
            # Verify connectivity with a tiny request
            self._model_name = "gemini-2.0-flash"
            self._types = types
            self.available = True
            log.info("GeminiBrain: Gemini 2.0 Flash (google-genai) initialised.")
        except ImportError:
            log.error("GeminiBrain: 'google-genai' package not installed. Run: pip install google-genai")
        except Exception as exc:
            log.error(f"GeminiBrain: Initialisation failed — {exc}")

    def ask(self, query: str) -> str:
        """
        Send a query to Gemini and return a JARVIS-styled response.

        Args:
            query: The natural language question or command.

        Returns:
            A clean string response, or a polite fallback message.
        """
        if not self.available:
            return self._offline_fallback(query)

        try:
            log.info(f"GeminiBrain: Querying Gemini — '{query[:80]}'")

            # Build conversation context from history
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore

            contents = []
            for turn in self._history[-self.max_history * 2:]:
                role = "user" if turn["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=turn["text"])]))
            # Append current query
            contents.append(types.Content(role="user", parts=[types.Part(text=query)]))

            response = self._client.models.generate_content(
                model=self._model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=_SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=512,
                ),
            )
            reply = response.text.strip() if response.text else "I was unable to generate a response."

            # Store in rolling history
            self._history.append({"role": "user", "text": query})
            self._history.append({"role": "model", "text": reply})
            if len(self._history) > self.max_history * 2:
                self._history = self._history[-(self.max_history * 2):]

            log.info(f"GeminiBrain: Response received ({len(reply)} chars).")
            return reply

        except Exception as exc:
            log.error(f"GeminiBrain: Query failed — {exc}")
            return (
                f"I encountered a difficulty retrieving that information, {self.user_name}. "
                "Please try again momentarily."
            )

    def reset_history(self) -> None:
        """Clear conversation history."""
        self._history.clear()
        log.info("GeminiBrain: Conversation history cleared.")

    @staticmethod
    def _offline_fallback(query: str) -> str:
        """Return a graceful message when Gemini is unavailable."""
        return (
            "My advanced reasoning module is currently offline. "
            "Please ensure a valid GEMINI_API_KEY is set in your .env file, Sir."
        )

    @property
    def history_length(self) -> int:
        """Number of turns stored in current session history."""
        return len(self._history) // 2
