"""Ollama coach with Socratic questioning behavior."""

import json
import requests
from typing import List
from backend.models import TranscriptEvent
from backend.coaches.base_coach import BaseCoach, SOCRATIC_PROMPT


class OllamaCoach(BaseCoach):
    """Ollama-based Socratic coach."""
    
    def __init__(self, ollama_url: str = None, model: str = None):
        """Initialize Ollama coach.
        
        Args:
            ollama_url: URL of Ollama server (defaults to Config.OLLAMA_URL)
            model: Model name to use (defaults to Config.OLLAMA_MODEL)
        """
        super().__init__()
        from backend.config import Config
        self.ollama_url = ollama_url or Config.OLLAMA_URL
        self.model = model or Config.OLLAMA_MODEL
    
    def chat(self, user_message: str, transcript_context: List[TranscriptEvent] = None) -> str:
        """Send message to coach and get response.
        
        Args:
            user_message: User's message
            transcript_context: Recent transcript events for context
        
        Returns:
            Assistant's response text
        """
        # Build context prompt using base class helper
        full_prompt = self._build_context_prompt(user_message, transcript_context)
        
        # Add to conversation history
        self._add_to_history("user", user_message)
        
        # Call Ollama
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=90
            )
            response.raise_for_status()
            result = response.json()
            assistant_text = result.get("response", "I'm having trouble responding right now.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                assistant_text = f"Error: Model '{self.model}' not found. Please check your OLLAMA_MODEL setting or install the model with: ollama pull {self.model}"
            else:
                assistant_text = f"HTTP Error {e.response.status_code}: {str(e)}"
            print(f"Ollama API error: {e}")
        except requests.exceptions.ConnectionError as e:
            assistant_text = f"Error: Cannot connect to Ollama at {self.ollama_url}. Please ensure Ollama is running."
            print(f"Ollama connection error: {e}")
        except Exception as e:
            assistant_text = f"Error: {str(e)}"
            print(f"Unexpected error calling Ollama: {e}")
        
        # Add to conversation history
        self._add_to_history("assistant", assistant_text)
        
        return assistant_text

    def generate_signals(
        self,
        transcript_events: List[TranscriptEvent],
        prior_signals: List[dict],
    ) -> List[dict]:
        """Generate coaching signals based on transcript events."""
        transcript_payload = [
            {
                "stream": event.stream,
                "text": event.text,
                "ts": event.ts,
            }
            for event in transcript_events[-30:]
            if event.is_final
        ]
        prompt = (
            "You are a gentle Socratic coach that detects four signal types:\n"
            "reasoning (weak inference/overgeneralization/fallacy risk),\n"
            "accountability (question not answered/dodged),\n"
            "language (loaded or ambiguous term),\n"
            "drift (topic shift/tangent).\n\n"
            "Rules:\n"
            "- Never accuse intent.\n"
            "- Use coach-like, supportive language.\n"
            "- Only use evidence present in the transcript.\n"
            "- Return STRICT JSON only, no markdown.\n"
            "- Output object format: {\"signals\": [ ... ]}\n"
            "- Each signal should include kind, confidence (0-1), title, detail, evidence, suggested.\n"
            "- Evidence items: {\"stream\":\"A\"|\"B\", \"quote\": str, \"ts\": float|null}\n"
            "- Suggested keys vary by kind:\n"
            "  reasoning: socratic_question, explain\n"
            "  accountability: reask, narrow, direct\n"
            "  language: define_term, examples\n"
            "  drift: refocus, summarize\n\n"
            "Recent transcript events (final only):\n"
            f"{json.dumps(transcript_payload, ensure_ascii=False)}\n\n"
            "Recent signals to avoid repeating:\n"
            f"{json.dumps(prior_signals, ensure_ascii=False)}\n\n"
            "Return JSON now."
        )

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=90,
            )
            response.raise_for_status()
            result = response.json()
            raw_text = result.get("response", "")
        except Exception as exc:
            print(f"Ollama signal generation error: {exc}")
            return []

        parsed = self._extract_json(raw_text)
        if not parsed or "signals" not in parsed:
            return []
        signals = parsed.get("signals")
        return signals if isinstance(signals, list) else []
