"""Test database operations."""

import os
import tempfile
from datetime import datetime
from database import SessionDatabase, initialize_database


def test_database_operations():
    """Test basic database operations."""
    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Initialize database
        print(f"Initializing database at {db_path}")
        initialize_database(db_path)
        
        # Create SessionDatabase instance
        db = SessionDatabase(db_path)
        print("✓ Database initialized successfully")
        
        # Test create_session
        feedback_data = {
            'themes': ['communication', 'leadership'],
            'comments': ['Great team player', 'Could improve delegation']
        }
        session_id = db.create_session('user123', feedback_data)
        print(f"✓ Created session with ID: {session_id}")
        
        # Test save_development_plan
        goals = [
            {
                'goal_text': 'Improve delegation skills',
                'goal_type': 'start',
                'specific_behavior': 'Delegate at least one task per week',
                'measurable_criteria': 'Track delegated tasks in weekly log',
                'target_date': '2025-12-31',
                'action_steps': ['Identify tasks to delegate', 'Schedule delegation meetings']
            },
            {
                'goal_text': 'Continue strong communication',
                'goal_type': 'continue',
                'specific_behavior': 'Maintain weekly team updates',
                'measurable_criteria': 'Weekly update emails sent',
                'target_date': '2025-12-31',
                'action_steps': ['Keep current schedule', 'Gather feedback']
            }
        ]
        db.save_development_plan(session_id, goals)
        print(f"✓ Saved {len(goals)} goals to development plan")
        
        # Test record_emotion_event
        db.record_emotion_event(
            session_id=session_id,
            emotion_type='neutral',
            confidence=0.85,
            r2c2_phase='relationship',
            audio_features={'pitch': 150.0, 'energy': 0.6}
        )
        db.record_emotion_event(
            session_id=session_id,
            emotion_type='defensive',
            confidence=0.72,
            r2c2_phase='reaction',
            audio_features={'pitch': 180.0, 'energy': 0.8}
        )
        print("✓ Recorded emotion events")
        
        # Test record_phase_transition
        db.record_phase_transition(
            session_id=session_id,
            from_phase='relationship',
            to_phase='reaction',
            trigger_reason='Time threshold reached',
            time_in_previous_phase=180.5
        )
        print("✓ Recorded phase transition")
        
        # Test get_user_sessions
        sessions = db.get_user_sessions('user123')
        assert len(sessions) == 1
        assert sessions[0]['session_id'] == session_id
        print(f"✓ Retrieved {len(sessions)} session(s) for user")
        
        # Test get_session_summary
        summary = db.get_session_summary(session_id)
        assert summary is not None
        assert summary['session_id'] == session_id
        assert len(summary['development_plan']) == 2
        assert len(summary['emotion_events']) == 2
        assert len(summary['phase_transitions']) == 1
        print("✓ Retrieved complete session summary")
        print(f"  - Development plan: {len(summary['development_plan'])} goals")
        print(f"  - Emotion events: {len(summary['emotion_events'])} events")
        print(f"  - Phase transitions: {len(summary['phase_transitions'])} transitions")
        
        # Test mark_goal_complete
        goal_id = summary['development_plan'][0]['goal_id']
        success = db.mark_goal_complete(goal_id)
        assert success
        print(f"✓ Marked goal {goal_id} as complete")
        
        # Verify goal completion
        updated_summary = db.get_session_summary(session_id)
        completed_goal = [g for g in updated_summary['development_plan'] if g['goal_id'] == goal_id][0]
        assert completed_goal['is_completed'] == True
        assert completed_goal['completed_at'] is not None
        print("✓ Verified goal completion status")
        
        # Test end_session
        session_summary = {
            'duration': 1200,
            'key_insights': ['Improved self-awareness', 'Clear action plan'],
            'next_steps': ['Follow up in 30 days']
        }
        db.end_session(session_id, session_summary)
        print("✓ Ended session with summary")
        
        # Verify session ended
        final_session = db.get_session_by_id(session_id)
        assert final_session['end_time'] is not None
        assert final_session['session_summary'] is not None
        print("✓ Verified session end time and summary")
        
        print("\n✅ All database operations completed successfully!")
        
    finally:
        # Clean up temporary database
        if os.path.exists(db_path):
            os.unlink(db_path)
            print(f"\n🧹 Cleaned up temporary database")


if __name__ == '__main__':
    test_database_operations()
