"""API routes for R2C2 Voice Coach."""

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from api.models import (
    StartSessionRequest,
    StartSessionResponse,
    SessionHistoryResponse,
    SessionDetailResponse,
    GoalCompleteResponse,
    FeedbackUploadRequest,
    FeedbackUploadResponse,
    FeedbackTheme,
)
from api.feedback_parser import parse_feedback


# Create API router
router = APIRouter()


def get_db():
    """Get database instance from app state."""
    from api.server import db
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized"
        )
    return db


@router.get("/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "R2C2 Voice Coach API",
        "version": "0.1.0",
        "endpoints": {
            "start_session": "POST /api/start",
            "session_history": "GET /api/sessions/{user_id}",
            "session_detail": "GET /api/session/{session_id}",
            "complete_goal": "PUT /api/goal/{goal_id}/complete",
            "upload_feedback": "POST /api/feedback/upload"
        }
    }


@router.post("/start", response_model=StartSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(request: StartSessionRequest):
    """
    Start a new R2C2 coaching session.
    
    Creates a new session in the database and returns Daily.co room credentials
    for establishing the WebRTC connection.
    
    Args:
        request: Session start request with user_id and feedback_data
        
    Returns:
        Session ID, room URL, and authentication token
    """
    db = get_db()
    
    try:
        # Create session in database
        session_id = db.create_session(
            user_id=request.user_id,
            feedback_data=request.feedback_data
        )
        
        logger.info(f"Created session {session_id} for user {request.user_id}")
        
        # Create Daily.co room for this session
        # In production, this would call Daily.co API to create a room
        # For MVP, we'll use environment variables or a default room
        import os
        from datetime import datetime, timedelta
        
        # Generate room URL (in production, create via Daily.co API)
        daily_domain = os.getenv("DAILY_DOMAIN", "your-domain.daily.co")
        room_name = f"r2c2-session-{session_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        room_url = f"https://{daily_domain}/{room_name}"
        
        # Generate token (in production, create via Daily.co API with proper expiration)
        # For MVP, we'll return a placeholder that the bot starter will handle
        token = os.getenv("DAILY_API_KEY", "placeholder-token")
        
        return StartSessionResponse(
            session_id=session_id,
            room_url=room_url,
            token=token,
            message=f"Session {session_id} created successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/sessions/{user_id}", response_model=SessionHistoryResponse)
async def get_session_history(user_id: str):
    """
    Get session history for a user.
    
    Returns a list of all sessions for the specified user, including
    basic information like start/end times.
    
    Args:
        user_id: The user identifier
        
    Returns:
        List of session summaries
    """
    db = get_db()
    
    try:
        sessions = db.get_user_sessions(user_id)
        
        logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")
        
        return SessionHistoryResponse(
            user_id=user_id,
            sessions=[
                SessionSummaryItem(**session) for session in sessions
            ],
            total_sessions=len(sessions)
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve session history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session history: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(session_id: int):
    """
    Get detailed information for a specific session.
    
    Returns comprehensive session data including:
    - Session metadata
    - Feedback data
    - Development plan goals
    - Emotion events
    - Phase transitions
    - Session summary
    
    Args:
        session_id: The session identifier
        
    Returns:
        Detailed session information
    """
    db = get_db()
    
    try:
        session_data = db.get_session_summary(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        logger.info(f"Retrieved detailed data for session {session_id}")
        
        return SessionDetailResponse(
            session_id=session_data['session_id'],
            user_id=session_data['user_id'],
            start_time=session_data['start_time'],
            end_time=session_data.get('end_time'),
            feedback_data=session_data.get('feedback_data'),
            session_summary=session_data.get('session_summary'),
            development_plan=[Goal(**goal) for goal in session_data.get('development_plan', [])],
            emotion_events=[EmotionEvent(**event) for event in session_data.get('emotion_events', [])],
            phase_transitions=[PhaseTransition(**trans) for trans in session_data.get('phase_transitions', [])]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve session detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session detail: {str(e)}"
        )


@router.put("/goal/{goal_id}/complete", response_model=GoalCompleteResponse)
async def mark_goal_complete(goal_id: int):
    """
    Mark a development plan goal as completed.
    
    Updates the goal's completion status and records the completion timestamp.
    
    Args:
        goal_id: The goal identifier
        
    Returns:
        Success status and completion details
    """
    db = get_db()
    
    try:
        from datetime import datetime
        
        success = db.mark_goal_complete(goal_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Goal {goal_id} not found"
            )
        
        completed_at = datetime.now().isoformat()
        
        logger.info(f"Marked goal {goal_id} as complete")
        
        return GoalCompleteResponse(
            success=True,
            goal_id=goal_id,
            completed_at=completed_at,
            message=f"Goal {goal_id} marked as complete"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark goal complete: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark goal complete: {str(e)}"
        )


@router.post("/feedback/upload", response_model=FeedbackUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_feedback(request: FeedbackUploadRequest):
    """
    Upload and parse 360° feedback data.
    
    Accepts feedback in multiple formats:
    - Raw text input
    - CSV file (base64 encoded)
    - JSON file (base64 encoded)
    
    Parses the feedback to extract themes, categories, and sentiment.
    
    Args:
        request: Feedback upload request with user_id and feedback data
        
    Returns:
        Parsed feedback structure with themes and comments
    """
    try:
        from datetime import datetime
        import base64
        
        # Decode file content if provided
        file_content = None
        if request.feedback_file:
            try:
                file_content = base64.b64decode(request.feedback_file).decode('utf-8')
            except Exception as e:
                logger.error(f"Failed to decode feedback file: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file encoding. Expected base64 encoded content."
                )
        
        # Parse feedback
        try:
            parsed_data = parse_feedback(
                feedback_text=request.feedback_text,
                feedback_file=file_content,
                file_type=request.file_type
            )
        except ValueError as e:
            logger.error(f"Failed to parse feedback: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Generate feedback ID
        feedback_id = f"feedback_{request.user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"Parsed feedback for user {request.user_id}: {len(parsed_data['themes'])} themes, {parsed_data['total_comments']} comments")
        
        return FeedbackUploadResponse(
            feedback_id=feedback_id,
            user_id=request.user_id,
            parsed_themes=[FeedbackTheme(**theme) for theme in parsed_data['themes']],
            total_comments=parsed_data['total_comments'],
            message=f"Successfully parsed {parsed_data['total_comments']} feedback comments into {len(parsed_data['themes'])} themes"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process feedback: {str(e)}"
        )
