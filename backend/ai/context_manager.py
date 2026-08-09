"""
context_manager.py
-------------------
Owns per-session interview state: the transcript, question/day counters, and
the current position in the plan built by topic_selector.py. Pure data/state
— no LLM calls, no HTTP. This is what makes the interview "remember" prior
answers across turns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .topic_selector import PlanItem


@dataclass
class Turn:
    role: str              # "interviewer" | "candidate"
    content: str
    day: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class InterviewContext:
    """One instance = one sessionId. Created on first request, mutated turn by turn."""

    MAX_FOLLOW_UPS_PER_DAY = 2
    MIN_QUESTIONS = 8
    MIN_DAYS = 4
    MAX_TOTAL_QUESTIONS = 14  # hard safety cap

    def __init__(self, session_id: str, candidate: Dict[str, Any]):
        self.session_id = session_id
        self.candidate = candidate

        self.plan: List[PlanItem] = []
        self.plan_index: int = 0

        self.transcript: List[Turn] = []
        self.questions_asked: int = 0
        self.days_covered: List[int] = []

        self.finished: bool = False

    def set_plan(self, plan: List[PlanItem]) -> None:
        self.plan = plan
        self.plan_index = 0

    @property
    def current_item(self) -> Optional[PlanItem]:
        if 0 <= self.plan_index < len(self.plan):
            return self.plan[self.plan_index]
        return None

    def advance_plan(self) -> Optional[PlanItem]:
        self.plan_index += 1
        return self.current_item

    def append_plan_item(self, item: PlanItem) -> PlanItem:
        """Used when the plan is exhausted but the minimum question/day bar
        hasn't been met yet — extends the plan on the fly (see
        topic_selector.pick_additional_day)."""
        self.plan.append(item)
        self.plan_index = len(self.plan) - 1
        return item

    def log_interviewer(self, content: str, day: Optional[int] = None) -> None:
        self.transcript.append(Turn(role="interviewer", content=content, day=day))

    def log_candidate(self, content: str, day: Optional[int] = None) -> None:
        self.transcript.append(Turn(role="candidate", content=content, day=day))

    def record_question(self, day: int, question: str) -> None:
        self.questions_asked += 1
        if day not in self.days_covered:
            self.days_covered.append(day)
        self.log_interviewer(question, day=day)
        item = self.current_item
        if item and item.day == day:
            item.opened = True
            item.exchanges.append({"question": question})

    def record_answer(self, day: int, answer: str) -> None:
        self.log_candidate(answer, day=day)
        item = self.current_item
        if item and item.day == day and item.exchanges:
            item.exchanges[-1]["answer"] = answer

    def plan_exhausted(self) -> bool:
        return self.plan_index >= len(self.plan)

    def min_bar_met(self) -> bool:
        return self.questions_asked >= self.MIN_QUESTIONS and len(self.days_covered) >= self.MIN_DAYS

    def hit_safety_cap(self) -> bool:
        return self.questions_asked >= self.MAX_TOTAL_QUESTIONS

    def should_end(self) -> bool:
        if self.hit_safety_cap():
            return True
        return self.plan_exhausted() and self.min_bar_met()

    def full_transcript_text(self) -> str:
        lines = []
        for t in self.transcript:
            speaker = "Interviewer" if t.role == "interviewer" else "Candidate"
            day_tag = f" [Day {t.day}]" if t.day else ""
            lines.append(f"{speaker}{day_tag}: {t.content}")
        return "\n".join(lines)