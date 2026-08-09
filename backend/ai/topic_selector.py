"""
topic_selector.py
------------------
Decides WHICH curriculum days to interview a candidate on, and WHY, based on
their mission history (candidates.json) crossed with the curriculum
(curriculum.json). This is the personalization engine — it's what makes the
interview feel tailored instead of generic.

Scoring priority (highest signal first):
    1. failed missions      -> most important: real, confirmed gap
    2. skipped missions     -> unknown gap, worth probing
    3. struggled-but-passed -> passed on attempt >= STRUGGLE_ATTEMPTS, likely shaky
    4. strong pass           -> passed in <= 2 attempts: used sparingly, to verify
                                 real depth rather than lucky memorization

We also enforce spread across curriculum modules so the interview doesn't
camp on one topic area (e.g. all RAG, no agentic/MCP), and cap how many
"strength check" days we include so the interview stays focused on gaps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

STRUGGLE_ATTEMPTS = 4          # attempts >= this on a passed mission counts as "struggled"
TARGET_PLAN_SIZE = 6           # how many days we aim to build the interview plan from
MAX_STRENGTH_CHECKS = 2        # cap on "they nailed it, verify depth" days


@dataclass
class PlanItem:
    day: int
    title: str
    type: str
    objectives: List[str]
    tools: List[str]
    reason: str            # "failed" | "skipped" | "struggled (N attempts)" | "strength (first-try pass)"
    priority: float

    opened: bool = False
    follow_ups_asked: int = 0
    exchanges: List[Dict[str, str]] = field(default_factory=list)


def _day_lookup(curriculum: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    return {d["day"]: d for d in curriculum.get("days", [])}


def _module_of_day(curriculum: Dict[str, Any], day: int) -> int:
    for m in curriculum.get("modules", []):
        lo, hi = m["days"][0], m["days"][-1]
        if lo <= day <= hi:
            return m["n"]
    return -1


def select_plan(candidate: Dict[str, Any], curriculum: Dict[str, Any]) -> List[PlanItem]:
    days_by_number = _day_lookup(curriculum)
    missions = candidate.get("missions", [])

    scored: List[PlanItem] = []

    for m in missions:
        day_num = m.get("day")
        day_info = days_by_number.get(day_num)
        if not day_info:
            continue  # mission references a day not in curriculum — skip defensively

        if m.get("skipped"):
            reason, priority = "skipped", 90
        elif m.get("passed") is False:
            reason, priority = "failed", 100
        elif m.get("passed") is True:
            attempts = m.get("attempts", 1)
            if attempts >= STRUGGLE_ATTEMPTS:
                reason, priority = f"struggled ({attempts} attempts)", 70
            else:
                reason, priority = "strength (first-try pass)", 30
        else:
            continue

        scored.append(PlanItem(
            day=day_num,
            title=day_info["title"],
            type=day_info.get("type", ""),
            objectives=day_info.get("objectives", []),
            tools=day_info.get("tools", []),
            reason=reason,
            priority=priority,
        ))

    # sort by priority (gaps first), highest first
    scored.sort(key=lambda p: p.priority, reverse=True)

    plan: List[PlanItem] = []
    modules_used: set = set()
    strength_count = 0

    # first pass: take top-priority items, enforcing module spread and strength cap
    for item in scored:
        if len(plan) >= TARGET_PLAN_SIZE:
            break
        if item.reason.startswith("strength"):
            if strength_count >= MAX_STRENGTH_CHECKS:
                continue
            strength_count += 1

        module = _module_of_day(curriculum, item.day)
        # allow at most 2 days per module in the plan, to keep coverage broad
        if sum(1 for p in plan if _module_of_day(curriculum, p.day) == module) >= 2:
            continue

        plan.append(item)
        modules_used.add(module)

    # second pass (fallback): if the module-spread rule left us short of the
    # minimum required days, backfill from remaining scored items ignoring
    # the module cap, so we always satisfy the >=4 distinct days requirement.
    if len(plan) < 4:
        chosen_days = {p.day for p in plan}
        for item in scored:
            if len(plan) >= max(4, TARGET_PLAN_SIZE):
                break
            if item.day in chosen_days:
                continue
            plan.append(item)
            chosen_days.add(item.day)

    # order the final plan: gaps (failed/skipped) first for early probing,
    # struggled next, strength checks last (nice way to end on a high note)
    order_weight = {"failed": 0, "skipped": 1}

    def sort_key(p: PlanItem):
        if p.reason in order_weight:
            return (order_weight[p.reason], -p.priority)
        if p.reason.startswith("struggled"):
            return (2, -p.priority)
        return (3, -p.priority)

    plan.sort(key=sort_key)
    return plan


def pick_additional_day(curriculum: Dict[str, Any], excluded_days: set) -> "PlanItem | None":
    """
    Safety-net used by interviewer.py: if the interview reaches the end of
    its planned days without yet hitting the required minimum (8 questions /
    4 days), pull in one more curriculum day the plan hasn't covered yet,
    so the hard minimum from the spec is guaranteed regardless of how many
    follow-ups the model chose to ask along the way.
    """
    for day_info in curriculum.get("days", []):
        day_num = day_info.get("day")
        if day_num in excluded_days:
            continue
        return PlanItem(
            day=day_num,
            title=day_info["title"],
            type=day_info.get("type", ""),
            objectives=day_info.get("objectives", []),
            tools=day_info.get("tools", []),
            reason="additional coverage",
            priority=0,
        )
    return None