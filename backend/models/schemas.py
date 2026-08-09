"""
schemas.py
----------
Pydantic models matching technical-spec.md exactly.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Optional[Dict[str, Any]] = None   # full candidate.json object, first request only
    message: Optional[str] = None                # candidate's answer, every request after that


class FeedbackResponse(BaseModel):
    summary: str
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    next: List[str] = Field(default_factory=list)


class InterviewResponse(BaseModel):
    reply: str
    done: bool = False
    feedback: Optional[FeedbackResponse] = None