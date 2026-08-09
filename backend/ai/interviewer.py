"""
interviewer.py
---------------
The AI orchestrator. This is the ONLY module the API layer (routes/) needs
to import. Exposes exactly two methods, mapping 1:1 onto the two request
shapes in technical-spec.md:

    POST /api/interview {sessionId, candidate}  -> Interviewer.start(session_id, candidate)
    POST /api/interview {sessionId, message}     -> Interviewer.respond(session_id, message)

Both return a dict ready to hand straight back as the HTTP JSON response:

    {"reply": str, "done": bool}
    {"reply": str, "done": True, "feedback": {"summary","strengths","gaps","next"}}

Session state (which curriculum days to cover, transcript, counters) lives
entirely inside this class's `self.sessions` dict, keyed by sessionId — no
external state object needs to be threaded through by the caller.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .context_manager import InterviewContext
from .topic_selector import select_plan, pick_additional_day
from .question_generator import generate_opening_question, decide_next
from .evaluator import generate_feedback
from .prompts.question_prompt import build_welcome_message
from .llm_client import build_default_llm_client

_DEFAULT_CURRICULUM_PATH = Path(__file__).resolve().parent.parent / "data" / "curriculum.json"


def _load_curriculum(path: Path) -> Dict[str, Any]:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: curriculum.json not found at {path}")
        return {"days": [], "modules": []}


class Interviewer:
    def __init__(self, curriculum: Optional[Dict[str, Any]] = None, llm_client: Optional[Any] = None):
        """
        curriculum: pass in already-loaded curriculum.json content (e.g. from
                    services/data_loader.py) to avoid loading the file twice.
                    If omitted, loads it directly from backend/data/curriculum.json.
        llm_client: object exposing .complete(messages) -> str. If omitted,
                    builds the default Anthropic-backed client (see llm_client.py).
        """
        self.curriculum = curriculum if curriculum is not None else _load_curriculum(_DEFAULT_CURRICULUM_PATH)
        self.llm = llm_client if llm_client is not None else build_default_llm_client()
        self.sessions: Dict[str, InterviewContext] = {}

    # ------------------------------------------------------------------
    # POST /api/interview  { sessionId, candidate }
    # ------------------------------------------------------------------

    def start(self, session_id: str, candidate: Dict[str, Any]) -> Dict[str, Any]:
        context = InterviewContext(session_id, candidate)
        plan = select_plan(candidate, self.curriculum)
        context.set_plan(plan)
        self.sessions[session_id] = context

        welcome = build_welcome_message(candidate)
        first_item = context.current_item

        if first_item is None:
            # Candidate has no usable mission history — still satisfy the
            # contract rather than erroring out.
            context.finished = True
            feedback = generate_feedback(self.llm, candidate, context)
            return {
                "reply": welcome + " It looks like there isn't enough mission history to "
                                    "build an interview for this candidate.",
                "done": True,
                "feedback": feedback,
            }

        first_question = generate_opening_question(self.llm, candidate, first_item)
        context.record_question(first_item.day, first_question)

        return {"reply": f"{welcome} {first_question}", "done": False}

    # ------------------------------------------------------------------
    # POST /api/interview  { sessionId, message }
    # ------------------------------------------------------------------

    def respond(self, session_id: str, message: str) -> Dict[str, Any]:
        context = self.sessions.get(session_id)

        if context is None:
            # No prior state for this session (routes.py should normally
            # catch this and return 404 before calling respond() at all —
            # this is a defensive fallback, not the primary error path).
            return {
                "reply": "This interview session was not found. Please start a new interview.",
                "done": True,
                "feedback": {"summary": "Session not found.", "strengths": [], "gaps": [], "next": []},
            }

        if context.finished:
            return {
                "reply": "This interview has already ended.",
                "done": True,
                "feedback": generate_feedback(self.llm, context.candidate, context),
            }

        item = context.current_item
        if item is None:
            return self._finish(context)

        context.record_answer(item.day, message)
        decision = decide_next(self.llm, context.candidate, item, InterviewContext.MAX_FOLLOW_UPS_PER_DAY)

        if decision["action"] == "follow_up":
            item.follow_ups_asked += 1
            context.record_question(item.day, decision["question"])
            return {"reply": decision["question"], "done": False}

        # action == "advance"
        next_item = context.advance_plan()

        if next_item is None and not context.min_bar_met() and not context.hit_safety_cap():
            # Plan ran out before the spec's hard minimum (>=8 questions,
            # >=4 days) was met — pull in one more curriculum day rather
            # than ending early.
            excluded = {p.day for p in context.plan}
            extra = pick_additional_day(self.curriculum, excluded)
            if extra is not None:
                next_item = context.append_plan_item(extra)

        if context.should_end() or next_item is None:
            return self._finish(context, transition_line=decision["question"])

        next_question = generate_opening_question(self.llm, context.candidate, next_item)
        context.record_question(next_item.day, next_question)

        reply = f"{decision['question']} {next_question}".strip()
        return {"reply": reply, "done": False}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _finish(self, context: InterviewContext, transition_line: str = "") -> Dict[str, Any]:
        context.finished = True
        feedback = generate_feedback(self.llm, context.candidate, context)
        closing = "That covers everything I wanted to dig into. Interview completed — thank you."
        reply = f"{transition_line} {closing}".strip()
        return {"reply": reply, "done": True, "feedback": feedback}