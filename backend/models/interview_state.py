from datetime import datetime
from typing import Dict, Any
from .schemas import InterviewState, Question

class StateManager:
    """Helper to manage interview state"""
    
    @staticmethod
    def create_initial_state(session_id: str, candidate_data: Dict) -> InterviewState:
        """Create initial state when interview starts"""
        return InterviewState(
            session_id=session_id,
            candidate_id=candidate_data.get("member", {}).get("id", ""),
            candidate_data=candidate_data,
            questions_asked=[],
            answers=[],
            topics_covered=[],
            current_phase="introduction",
            done=False
        )
    
    @staticmethod
    def add_question(state: InterviewState, question: str, day: int = None, topic: str = None):
        """Add a question to the state"""
        state.questions_asked.append(
            Question(
                question=question,
                day=day,
                topic=topic,
                timestamp=datetime.now()
            )
        )
        state.updated_at = datetime.now()
        return state
    
    @staticmethod
    def add_answer(state: InterviewState, answer: str):
        """Add an answer to the state"""
        last_question = state.questions_asked[-1].question if state.questions_asked else "unknown"
        state.answers.append({
            "question": last_question,
            "answer": answer,
            "timestamp": datetime.now()
        })
        state.updated_at = datetime.now()
        return state
    
    @staticmethod
    def mark_done(state: InterviewState):
        """Mark interview as complete"""
        state.done = True
        state.updated_at = datetime.now()
        return state