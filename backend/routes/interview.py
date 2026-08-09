from fastapi import APIRouter, HTTPException
from models.schemas import InterviewRequest, InterviewResponse, FeedbackResponse
from services.session_manager import SessionManager
from services.data_loader import DataLoader
from services.ai_integration import AIIntegration
from models.interview_state import StateManager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
session_manager = SessionManager()
data_loader = DataLoader()
ai_integration = AIIntegration()

@router.post("/api/interview", response_model=InterviewResponse)
async def interview_endpoint(request: InterviewRequest):
    """
    Main interview endpoint.
    First request: Contains candidate data
    Subsequent requests: Contains message
    """
    try:
        session_id = request.sessionId
        
        # === CASE 1: First request (Starting interview) ===
        if request.candidate:
            logger.info(f"Starting new interview for candidate: {request.candidate.id}")
            
            # Get full candidate data from JSON
            candidate_data = data_loader.get_candidate(request.candidate.id)
            if not candidate_data:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Candidate {request.candidate.id} not found"
                )
            
            # Create session
            state = session_manager.create_session(session_id, candidate_data)
            
            # Initialize with AI
            ai_response = ai_integration.initialize_interview(candidate_data, session_id)
            
            # Add the first question to state
            if ai_response.get("reply"):
                state = StateManager.add_question(state, ai_response["reply"])
            
            session_manager.update_session(session_id, state)
            
            return InterviewResponse(
                reply=ai_response["reply"],
                done=False
            )
        
        # === CASE 2: Subsequent request (User message) ===
        elif request.message:
            logger.info(f"Processing message for session: {session_id}")
            
            # Get existing session
            state = session_manager.get_session(session_id)
            if not state:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Session {session_id} not found"
                )
            
            # Add user answer to state
            state = StateManager.add_answer(state, request.message)
            
            # Process through AI
            ai_response = ai_integration.process_message(state, request.message)
            
            # Add AI question to state
            if ai_response.get("reply"):
                state = StateManager.add_question(state, ai_response["reply"])
            
            session_manager.update_session(session_id, state)
            
            # Check if interview is complete
            done = ai_response.get("done", False)
            feedback = None
            
            if done:
                # Generate feedback
                feedback_data = ai_integration.generate_feedback(state)
                feedback = FeedbackResponse(
                    summary=feedback_data["summary"],
                    strengths=feedback_data["strengths"],
                    gaps=feedback_data["gaps"],
                    next=feedback_data["next"]
                )
                state = StateManager.mark_done(state)
                session_manager.update_session(session_id, state)
            
            return InterviewResponse(
                reply=ai_response["reply"],
                done=done,
                feedback=feedback
            )
        
        # === Invalid request ===
        else:
            raise HTTPException(
                status_code=400, 
                detail="Request must contain either 'candidate' or 'message'"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in interview endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error")

# Optional: Debug endpoint
@router.get("/api/interview/state/{session_id}")
async def get_interview_state(session_id: str):
    """Get the current state of an interview (for debugging)"""
    state = session_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": state.session_id,
        "candidate_id": state.candidate_id,
        "questions_asked": len(state.questions_asked),
        "answers_given": len(state.answers),
        "done": state.done
    }