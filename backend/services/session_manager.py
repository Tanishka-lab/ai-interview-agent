from typing import Dict, Optional
from models.schemas import InterviewState
from models.interview_state import StateManager

class SessionManager:
    """Manages interview sessions in memory"""
    
    def __init__(self):
        self.sessions: Dict[str, InterviewState] = {}
    
    def create_session(self, session_id: str, candidate_data: Dict) -> InterviewState:
        """Create a new session"""
        state = StateManager.create_initial_state(session_id, candidate_data)
        self.sessions[session_id] = state
        return state
    
    def get_session(self, session_id: str) -> Optional[InterviewState]:
        """Get an existing session"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, state: InterviewState) -> InterviewState:
        """Update an existing session"""
        self.sessions[session_id] = state
        return state
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        return session_id in self.sessions
    
    def delete_session(self, session_id: str):
        """Delete a session (cleanup)"""
        if session_id in self.sessions:
            del self.sessions[session_id]