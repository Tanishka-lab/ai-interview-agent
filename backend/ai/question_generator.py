"""
question_generator.py
-----------------------
Turns a chosen curriculum day (from topic_selector) plus the current
conversation state (from context_manager) into an actual message sent to
the candidate. Two responsibilities:

  1. generate_opening_question  -> first question for a new day in the plan
  2. decide_next                -> given the candidate's latest answer, either
                                    a) a follow-up question on the same day, or
                                    b) a transition line + move to the next day

Both call an injected `llm_client`, which must expose:

    llm_client.complete(messages: list[dict]) -> str

where `messages` is a list of {"role": "system"|"user", "content": str} and
the return value is the raw model text (str). This keeps this module
provider-agnostic.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict

from .prompts.question_prompt import build_question_messages
from .prompts.followup_prompt import build_followup_messages


def _extract_json(raw: str) -> Dict[str, Any]:
    """
    Tolerant JSON extraction: strips markdown fences if the model added them
    despite instructions, and falls back to grabbing the first {...} block.
    """
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    # Last-resort fallback so a single malformed LLM response never crashes
    # the interview — we just advance rather than getting stuck.
    return {"action": "advance", "question": "Understood — let's move to the next topic."}


def generate_opening_question(llm_client, candidate: Dict[str, Any], item) -> str:
    messages = build_question_messages(candidate, item)
    question = llm_client.complete(messages).strip()
    return question


def decide_next(llm_client, candidate: Dict[str, Any], item, max_follow_ups: int) -> Dict[str, str]:
    """
    Returns {"action": "follow_up" | "advance", "question": "<next message>"}.
    Caller (interviewer.py) is responsible for enforcing the follow-up
    cap and incrementing counters — this function just asks the model for a
    recommendation given the cap it was told about.
    """
    if item.follow_ups_asked >= max_follow_ups:
        # Don't even ask the model — we've hit the hard cap, force advance.
        return {"action": "advance", "question": "Good, let's move on."}

    messages = build_followup_messages(candidate, item, max_follow_ups)
    raw = llm_client.complete(messages)
    parsed = _extract_json(raw)

    action = parsed.get("action", "advance")
    if action not in ("follow_up", "advance"):
        action = "advance"
    question = parsed.get("question") or "Good, let's move on."

    return {"action": action, "question": question}