"""
routes/interview.py
--------------------
Implements the single required endpoint: POST /api/interview
plus GET /api/candidates and GET /api/interview/{id}/debug (convenience only).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from ai.interviewer import Interviewer
from models.schemas import InterviewRequest, InterviewResponse
from services.data_loader import DataLoader

logger = logging.getLogger(__name__)

router = APIRouter()

data_loader = DataLoader()
interviewer = Interviewer(curriculum=data_loader.curriculum)


@router.post("/api/interview", response_model=InterviewResponse)
async def interview_endpoint(request: InterviewRequest):
    try:
        if request.candidate is not None:
            logger.info("Starting new interview | session=%s", request.sessionId)
            result = interviewer.start(request.sessionId, request.candidate)
            return InterviewResponse(**result)

        if request.message is not None:
            if request.sessionId not in interviewer.sessions:
                raise HTTPException(
                    status_code=404,
                    detail=f"Session '{request.sessionId}' not found. Start a new interview first "
                           f"by sending a request with 'candidate'.",
                )
            logger.info("Continuing interview | session=%s", request.sessionId)
            result = interviewer.respond(request.sessionId, request.message)
            return InterviewResponse(**result)

        raise HTTPException(status_code=400, detail="Request must contain either 'candidate' or 'message'.")

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error in /api/interview | session=%s", request.sessionId)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/candidates")
async def list_candidates():
    return [
        {
            "id": c.get("member", {}).get("id"),
            "name": c.get("member", {}).get("name"),
            "jobRole": c.get("member", {}).get("jobRole"),
        }
        for c in data_loader.get_all_candidates()
    ]


@router.get("/api/interview/{session_id}/debug")
async def debug_session(session_id: str):
    context = interviewer.sessions.get(session_id)
    if context is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": context.session_id,
        "questions_asked": context.questions_asked,
        "days_covered": context.days_covered,
        "plan": [{"day": p.day, "title": p.title, "reason": p.reason} for p in context.plan],
        "finished": context.finished,
    }