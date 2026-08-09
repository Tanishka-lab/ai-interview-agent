"""
prompts/evaluation_prompt.py
------------------------------
Builds the prompt for the final structured feedback report, matching the
technical spec's required shape: {summary, strengths, gaps, next}.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_evaluation_messages(candidate: Dict[str, Any], context) -> List[Dict[str, str]]:
    member = candidate.get("member", {})
    name = member.get("name", "the candidate")

    days_list = ", ".join(f"Day {i.day} ({i.title})" for i in context.plan[: context.plan_index + 1])

    system = (
        "You are a senior technical interviewer writing an honest, specific, actionable "
        "post-interview evaluation. Base every point strictly on what the candidate actually "
        "said in the transcript below — do not invent claims they didn't make. Be direct but "
        "constructive, the way a good hiring manager would."
    )

    user = f"""Candidate: {name} ({member.get("jobRole", "")}, {member.get("yearsExperience", "?")} yrs experience)
Curriculum days covered in this interview: {days_list}

Full interview transcript:
{context.full_transcript_text()}

Write a final structured evaluation. Respond with STRICT JSON only, no markdown fences,
no extra commentary, in exactly this shape:
{{
  "summary": "<2-4 sentence overall assessment of technical communication and depth>",
  "strengths": ["<specific, evidence-based strength>", "..."],
  "gaps": ["<specific, evidence-based gap or weak spot>", "..."],
  "next": ["<concrete, actionable suggestion for what to review or practice next>", "..."]
}}

Keep each array to 2-5 concise, concrete bullet points grounded in specific moments from the transcript."""

    return [{"role": "system", "content": system}, {"role": "user", "content": user}]