"""
prompts/followup_prompt.py
----------------------------
Builds the prompt that decides, after each candidate answer, whether to
probe deeper on the current day (follow-up) or transition to the next
topic in the plan (advance). Asks the model for strict JSON so
question_generator.py can parse it deterministically.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .question_prompt import build_system_prompt


def build_followup_messages(candidate: Dict[str, Any], item, max_follow_ups: int) -> List[Dict[str, str]]:
    system = build_system_prompt(candidate)

    exchanges_text = "\n".join(
        f"Q: {ex.get('question', '')}\nA: {ex.get('answer', '')}" for ex in item.exchanges
    )

    user = f"""We are currently on Day {item.day}: "{item.title}".
Candidate signal for this day: {item.reason}.
Follow-ups already asked on this day: {item.follow_ups_asked} (max allowed: {max_follow_ups}).

Conversation so far on this day:
{exchanges_text}

Decide what to do next:
- "follow_up": the answer was vague, surface-level, avoided the hard part, or you can meaningfully
  probe deeper (e.g. ask them to justify a trade-off, handle an edge case, or explain what would break).
  Do NOT choose this if follow-ups already asked equals the max allowed.
- "advance": the answer was solid enough, already probed enough, or hit the follow-up limit —
  time to move to the next topic.

Respond with STRICT JSON only, no markdown fences, no extra text, in exactly this shape:
{{"action": "follow_up" or "advance", "question": "<the next message to send the candidate — either the follow-up question, or a brief natural one-line transition like 'Good, let's shift gears.' if advancing>"}}"""

    return [{"role": "system", "content": system}, {"role": "user", "content": user}]