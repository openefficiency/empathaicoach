"""Pydantic models for API request/response validation."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Request/Response models for session management

class StartSessionRequest(BaseModel):
    """Request model for starting a new session."""
    user_id: str = Field(..., description="Unique identifier for the user")
    feedback_data: Dict[str, Any] = Field(..., description="360° feedback data")


class StartSessionResponse(BaseModel):
    """Response model for session start."""
    session_id: int = Field(..., description="Unique session identifier")
    room_url: str = Field(..., description="Daily.co room URL for WebRTC connection")
    token: str = Field(..., description="Authentication token for the room")
    message: str = Field(default="Session created successfully")


class SessionSummaryItem(BaseModel):
    """Summary information for a single session."""
    session_id: int
    user_id: str
    start_time: str
    end_time: Optional[str] = None
    created_at: str


class SessionHistoryResponse(BaseModel):
    """Response model for user session history."""
    user_id: str
    sessions: List[SessionSummaryItem]
    total_sessions: int


class FeedbackTheme(BaseModel):
    """Feedback theme model."""
    category: str
    theme: str
    frequency: int
    examples: List[str]


class FeedbackComment(BaseModel):
    """Individual feedback comment."""
    source: str
    category: str
    comment: str
    sentiment: str


class Goal(BaseModel):
    """Development plan goal."""
    goal_id: int
    goal_text: str
    goal_type: str
    specific_behavior: str
    measurable_criteria: str
    target_date: Optional[str] = None
    action_steps: List[str]
    is_completed: bool
    completed_at: Optional[str] = None


class EmotionEvent(BaseModel):
    """Emotion detection event."""
    timestamp: str
    emotion_type: str
    confidence: float
    r2c2_phase: str
    audio_features: Optional[Dict[str, float]] = None


class PhaseTransition(BaseModel):
    """R2C2 phase transition event."""
    from_phase: str
    to_phase: str
    transition_time: str
    trigger_reason: str
    time_in_previous_phase: float


class SessionDetailResponse(BaseModel):
    """Detailed session information."""
    session_id: int
    user_id: str
    start_time: str
    end_time: Optional[str] = None
    feedback_data: Optional[Dict[str, Any]] = None
    session_summary: Optional[Dict[str, Any]] = None
    development_plan: List[Goal]
    emotion_events: List[EmotionEvent]
    phase_transitions: List[PhaseTransition]


class GoalCompleteResponse(BaseModel):
    """Response for goal completion."""
    success: bool
    goal_id: int
    completed_at: str
    message: str


# Request/Response models for feedback upload

class FeedbackUploadRequest(BaseModel):
    """Request model for uploading feedback data."""
    user_id: str = Field(..., description="User identifier")
    feedback_text: Optional[str] = Field(None, description="Raw feedback text")
    feedback_file: Optional[str] = Field(None, description="Base64 encoded file content")
    file_type: Optional[str] = Field(None, description="File type: csv, json, or text")


class FeedbackUploadResponse(BaseModel):
    """Response model for feedback upload."""
    feedback_id: str
    user_id: str
    parsed_themes: List[FeedbackTheme]
    total_comments: int
    message: str
