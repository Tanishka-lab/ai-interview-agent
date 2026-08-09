"""
evaluator.py
------------
Produces the final structured feedback report, matching the technical
spec's required shape exactly:

    {
      "summary": str,
      "strengths": [str, ...],
      "gaps": [str, ...],
      "next": [str, ...]
    }

Same llm_client contract as question_generator.py:
    llm_client.complete(messages: list[dict]) -> str
"""

from __future__ import annotations

from typing import Any, Dict

from .prompts.evaluation_prompt import build_evaluation_messages
from .question_generator import _extract_json  # reuse the same tolerant JSON parser

REQUIRED_KEYS = ("summary", "strengths", "gaps", "next")


def _fallback_feedback(context) -> Dict[str, Any]:
    """
    Used only if the LLM call fails or returns unparseable output — ensures
    the API contract is still satisfied (spec requires this shape on every
    completed interview, no exceptions).
    """
    days = ", ".join(f"Day {i.day}" for i in context.plan[: context.plan_index + 1])
    return {
        "summary": f"Interview completed across {len(context.days_covered)} topics ({days}). "
                   f"Automatic evaluation could not be generated — please review the transcript manually.",
        "strengths": [],
        "gaps": [],
        "next": ["Review the full transcript for a manual assessment."],
    }


def generate_feedback(llm_client, candidate: Dict[str, Any], context) -> Dict[str, Any]:
    messages = build_evaluation_messages(candidate, context)

    try:
        raw = llm_client.complete(messages)
        parsed = _extract_json(raw)
    except Exception:
        return _fallback_feedback(context)

    if not all(k in parsed for k in REQUIRED_KEYS):
        return _fallback_feedback(context)

    # normalize types defensively so a slightly malformed model response
    # (e.g. a string instead of a list) never breaks the API contract
    def _as_str_list(v):
        if isinstance(v, list):
            return [str(x) for x in v]
        if v:
            return [str(v)]
        return []

    return {
        "summary": str(parsed.get("summary", "")).strip(),
        "strengths": _as_str_list(parsed.get("strengths")),
        "gaps": _as_str_list(parsed.get("gaps")),
        "next": _as_str_list(parsed.get("next")),
    }