from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==== Request/Response Models (Matches Technical Spec) ====

class CandidateInfo(BaseModel):
    """Candidate data from first request"""
    id: str
    name: str
    jobRole: str
    yearsExperience: int
    education: str
    status: str

class InterviewRequest(BaseModel):
    """Combined request (handles both first and subsequent requests)"""
    sessionId: str
    candidate: Optional[CandidateInfo] = None
    message: Optional[str] = None

class FeedbackResponse(BaseModel):
    """Final feedback structure"""
    summary: str
    strengths: List[str]
    gaps: List[str]
    next: List[str]

class InterviewResponse(BaseModel):
    """API response format"""
    reply: str
    done: bool = False
    feedback: Optional[FeedbackResponse] = None

# ==== Internal State Models ====

class Question(BaseModel):
    """Track questions asked"""
    question: str
    day: Optional[int] = None
    topic: Optional[str] = None
    timestamp: datetime = datetime.now()

class InterviewState(BaseModel):
    """Full interview state"""
    session_id: str
    candidate_id: str
    candidate_data: Dict[str, Any] = {}
    questions_asked: List[Question] = []
    answers: List[Dict[str, Any]] = []
    topics_covered: List[int] = []
    current_phase: str = "introduction"
    done: bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()