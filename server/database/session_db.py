"""Session database operations for R2C2 Voice Coach."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager


class SessionDatabase:
    """Database interface for managing R2C2 coaching sessions."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the session database.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses default location.
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / "data" / "r2c2_coach.db")
        
        self.db_path = db_path
        
        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize schema if needed
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure the database schema exists."""
        from .schema import get_schema_sql
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(get_schema_sql())
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def create_session(self, user_id: str, feedback_data: Dict[str, Any]) -> int:
        """
        Create a new coaching session.
        
        Args:
            user_id: Unique identifier for the user
            feedback_data: Dictionary containing 360° feedback data
            
        Returns:
            The session ID of the newly created session
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO sessions (user_id, start_time, feedback_data)
                VALUES (?, ?, ?)
                """,
                (user_id, datetime.now().isoformat(), json.dumps(feedback_data))
            )
            conn.commit()
            return cursor.lastrowid
    
    def end_session(self, session_id: int, summary: Dict[str, Any]):
        """
        End a coaching session and save the summary.
        
        Args:
            session_id: The session ID to end
            summary: Dictionary containing session summary data
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE sessions
                SET end_time = ?, session_summary = ?, updated_at = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(), json.dumps(summary), datetime.now().isoformat(), session_id)
            )
            conn.commit()
    
    def save_development_plan(self, session_id: int, goals: List[Dict[str, Any]]):
        """
        Save development plan goals for a session.
        
        Args:
            session_id: The session ID
            goals: List of goal dictionaries with keys: goal_text, goal_type, 
                   specific_behavior, measurable_criteria, target_date, action_steps
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for goal in goals:
                cursor.execute(
                    """
                    INSERT INTO development_plans 
                    (session_id, goal_text, goal_type, specific_behavior, 
                     measurable_criteria, target_date, action_steps)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        goal.get('goal_text', ''),
                        goal.get('goal_type', 'start'),
                        goal.get('specific_behavior', ''),
                        goal.get('measurable_criteria', ''),
                        goal.get('target_date'),
                        json.dumps(goal.get('action_steps', []))
                    )
                )
            
            conn.commit()
    
    def record_emotion_event(
        self, 
        session_id: int, 
        emotion_type: str, 
        confidence: float,
        r2c2_phase: str,
        audio_features: Optional[Dict[str, float]] = None
    ):
        """
        Record an emotion detection event.
        
        Args:
            session_id: The session ID
            emotion_type: Type of emotion detected (neutral, defensive, frustrated, sad, anxious, positive)
            confidence: Confidence score (0.0 to 1.0)
            r2c2_phase: Current R2C2 phase (relationship, reaction, content, coaching)
            audio_features: Optional dictionary of audio features
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO emotion_events 
                (session_id, timestamp, emotion_type, confidence, r2c2_phase, audio_features)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    datetime.now().isoformat(),
                    emotion_type,
                    confidence,
                    r2c2_phase,
                    json.dumps(audio_features) if audio_features else None
                )
            )
            conn.commit()
    
    def record_phase_transition(
        self,
        session_id: int,
        from_phase: str,
        to_phase: str,
        trigger_reason: str,
        time_in_previous_phase: float
    ):
        """
        Record an R2C2 phase transition.
        
        Args:
            session_id: The session ID
            from_phase: The phase transitioning from
            to_phase: The phase transitioning to
            trigger_reason: Reason for the transition
            time_in_previous_phase: Time spent in previous phase (seconds)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO phase_transitions 
                (session_id, from_phase, to_phase, transition_time, trigger_reason, time_in_previous_phase)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    from_phase,
                    to_phase,
                    datetime.now().isoformat(),
                    trigger_reason,
                    time_in_previous_phase
                )
            )
            conn.commit()

    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of session dictionaries with basic information
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, start_time, end_time, created_at
                FROM sessions
                WHERE user_id = ?
                ORDER BY start_time DESC
                """,
                (user_id,)
            )
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row['id'],
                    'user_id': row['user_id'],
                    'start_time': row['start_time'],
                    'end_time': row['end_time'],
                    'created_at': row['created_at']
                })
            
            return sessions
    
    def get_session_summary(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed summary for a specific session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Dictionary containing session details, development plan, emotions, and phase transitions
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get session basic info
            cursor.execute(
                """
                SELECT id, user_id, start_time, end_time, feedback_data, session_summary
                FROM sessions
                WHERE id = ?
                """,
                (session_id,)
            )
            
            row = cursor.fetchone()
            if not row:
                return None
            
            session_data = {
                'session_id': row['id'],
                'user_id': row['user_id'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'feedback_data': json.loads(row['feedback_data']) if row['feedback_data'] else None,
                'session_summary': json.loads(row['session_summary']) if row['session_summary'] else None
            }
            
            # Get development plan
            cursor.execute(
                """
                SELECT id, goal_text, goal_type, specific_behavior, measurable_criteria,
                       target_date, action_steps, is_completed, completed_at
                FROM development_plans
                WHERE session_id = ?
                ORDER BY created_at
                """,
                (session_id,)
            )
            
            goals = []
            for goal_row in cursor.fetchall():
                goals.append({
                    'goal_id': goal_row['id'],
                    'goal_text': goal_row['goal_text'],
                    'goal_type': goal_row['goal_type'],
                    'specific_behavior': goal_row['specific_behavior'],
                    'measurable_criteria': goal_row['measurable_criteria'],
                    'target_date': goal_row['target_date'],
                    'action_steps': json.loads(goal_row['action_steps']) if goal_row['action_steps'] else [],
                    'is_completed': bool(goal_row['is_completed']),
                    'completed_at': goal_row['completed_at']
                })
            
            session_data['development_plan'] = goals
            
            # Get emotion events
            cursor.execute(
                """
                SELECT timestamp, emotion_type, confidence, r2c2_phase, audio_features
                FROM emotion_events
                WHERE session_id = ?
                ORDER BY timestamp
                """,
                (session_id,)
            )
            
            emotions = []
            for emotion_row in cursor.fetchall():
                emotions.append({
                    'timestamp': emotion_row['timestamp'],
                    'emotion_type': emotion_row['emotion_type'],
                    'confidence': emotion_row['confidence'],
                    'r2c2_phase': emotion_row['r2c2_phase'],
                    'audio_features': json.loads(emotion_row['audio_features']) if emotion_row['audio_features'] else None
                })
            
            session_data['emotion_events'] = emotions
            
            # Get phase transitions
            cursor.execute(
                """
                SELECT from_phase, to_phase, transition_time, trigger_reason, time_in_previous_phase
                FROM phase_transitions
                WHERE session_id = ?
                ORDER BY transition_time
                """,
                (session_id,)
            )
            
            transitions = []
            for trans_row in cursor.fetchall():
                transitions.append({
                    'from_phase': trans_row['from_phase'],
                    'to_phase': trans_row['to_phase'],
                    'transition_time': trans_row['transition_time'],
                    'trigger_reason': trans_row['trigger_reason'],
                    'time_in_previous_phase': trans_row['time_in_previous_phase']
                })
            
            session_data['phase_transitions'] = transitions
            
            return session_data
    
    def mark_goal_complete(self, goal_id: int) -> bool:
        """
        Mark a development plan goal as completed.
        
        Args:
            goal_id: The goal ID to mark as complete
            
        Returns:
            True if the goal was found and updated, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE development_plans
                SET is_completed = TRUE, completed_at = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(), goal_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get basic session information by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            Dictionary with session information or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, start_time, end_time, feedback_data, session_summary
                FROM sessions
                WHERE id = ?
                """,
                (session_id,)
            )
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'session_id': row['id'],
                'user_id': row['user_id'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'feedback_data': json.loads(row['feedback_data']) if row['feedback_data'] else None,
                'session_summary': json.loads(row['session_summary']) if row['session_summary'] else None
            }
    
    def update_session_state(self, session_id: int, state_data: Dict[str, Any]):
        """
        Update session with current state data (for recovery/reconnection).
        
        Args:
            session_id: The session ID
            state_data: Dictionary containing current session state
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE sessions
                SET session_summary = ?, updated_at = ?
                WHERE id = ?
                """,
                (json.dumps(state_data), datetime.now().isoformat(), session_id)
            )
            conn.commit()
