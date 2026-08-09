"""
llm_client.py
--------------
Thin wrapper around Anthropic's Messages API exposing the single method
question_generator.py / evaluator.py rely on:

    llm_client.complete(messages: list[{"role": str, "content": str}]) -> str

Reads ANTHROPIC_API_KEY from the environment (loaded via .env if present —
requires `python-dotenv`). If no key is found, falls back to a safe
placeholder response instead of crashing, so the app still boots for local
dev / demo without secrets configured.
"""

from __future__ import annotations

import os
from typing import Dict, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class LLMClient:
    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 500):
        self.model = model
        self.max_tokens = max_tokens
        self._client = None

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                print("Warning: 'anthropic' package not installed — run `pip install anthropic`. "
                      "Falling back to placeholder responses.")

    def complete(self, messages: List[Dict[str, str]]) -> str:
        if self._client is None:
            return self._fallback(messages)

        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        conversation = [m for m in messages if m["role"] != "system"]

        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=conversation,
        )
        return "".join(block.text for block in response.content if hasattr(block, "text")).strip()

    @staticmethod
    def _fallback(messages: List[Dict[str, str]]) -> str:
        # No API key configured — keep the app functional (e.g. for teammates
        # running the backend without secrets) rather than raising.
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        if '"action"' in last_user:  # follow-up decision prompt expects JSON
            return '{"action": "advance", "question": "Let\'s move on to the next topic."}'
        if '"summary"' in last_user:  # feedback prompt expects JSON
            return (
                '{"summary": "ANTHROPIC_API_KEY not configured — this is placeholder feedback.", '
                '"strengths": [], "gaps": [], "next": ["Configure ANTHROPIC_API_KEY to enable real evaluation."]}'
            )
        return "Can you walk me through how you approached that?"


def build_default_llm_client() -> LLMClient:
    return LLMClient()