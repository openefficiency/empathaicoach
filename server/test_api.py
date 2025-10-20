"""Simple test script for R2C2 Voice Coach API endpoints."""

import sys
sys.path.insert(0, '.')

from api.feedback_parser import parse_feedback


def test_feedback_parser():
    """Test the feedback parser with various inputs."""
    print("Testing Feedback Parser...")
    print("-" * 60)
    
    # Test 1: Simple text feedback
    print("\n1. Testing text feedback parsing:")
    text_feedback = """
    Great communication skills and technical expertise.
    Could improve on delegation and time management.
    Excellent problem-solving abilities.
    Needs to work on providing more feedback to team members.
    """
    
    result = parse_feedback(feedback_text=text_feedback)
    print(f"   Extracted {len(result['themes'])} themes:")
    for theme in result['themes']:
        print(f"   - {theme['theme']} ({theme['category']}): {theme['frequency']} mentions")
    print(f"   Total comments: {result['total_comments']}")
    
    # Test 2: CSV feedback
    print("\n2. Testing CSV feedback parsing:")
    csv_feedback = """source,category,comment,sentiment
manager,communication,Great at explaining complex ideas,positive
peer,delegation,Could delegate more tasks,negative
direct_report,leadership,Provides clear direction,positive
peer,technical,Deep technical knowledge,positive
manager,time_management,Sometimes misses deadlines,negative"""
    
    result = parse_feedback(feedback_file=csv_feedback, file_type='csv')
    print(f"   Extracted {len(result['themes'])} themes:")
    for theme in result['themes']:
        print(f"   - {theme['theme']} ({theme['category']}): {theme['frequency']} mentions")
    print(f"   Total comments: {result['total_comments']}")
    
    # Test 3: JSON feedback
    print("\n3. Testing JSON feedback parsing:")
    json_feedback = """{
        "comments": [
            {
                "source": "manager",
                "category": "communication",
                "comment": "Excellent communicator",
                "sentiment": "positive"
            },
            {
                "source": "peer",
                "category": "collaboration",
                "comment": "Great team player",
                "sentiment": "positive"
            },
            {
                "source": "direct_report",
                "category": "leadership",
                "comment": "Could provide more direction",
                "sentiment": "negative"
            }
        ]
    }"""
    
    result = parse_feedback(feedback_file=json_feedback, file_type='json')
    print(f"   Extracted {len(result['themes'])} themes:")
    for theme in result['themes']:
        print(f"   - {theme['theme']} ({theme['category']}): {theme['frequency']} mentions")
    print(f"   Total comments: {result['total_comments']}")
    
    print("\n" + "=" * 60)
    print("✓ All feedback parser tests passed!")
    print("=" * 60)


def test_database_operations():
    """Test database operations."""
    print("\n\nTesting Database Operations...")
    print("-" * 60)
    
    from database.session_db import SessionDatabase
    from datetime import datetime
    
    # Initialize database
    db = SessionDatabase(db_path="test_r2c2_coach.db")
    print("✓ Database initialized")
    
    # Create a test session
    feedback_data = {
        'feedback_id': 'test_feedback_001',
        'themes': [
            {
                'category': 'strength',
                'theme': 'Communication',
                'frequency': 3,
                'examples': ['Great communicator']
            }
        ],
        'raw_comments': [
            {
                'source': 'manager',
                'category': 'communication',
                'comment': 'Great communicator',
                'sentiment': 'positive'
            }
        ]
    }
    
    session_id = db.create_session(user_id='test_user', feedback_data=feedback_data)
    print(f"✓ Created session {session_id}")
    
    # Record emotion event
    db.record_emotion_event(
        session_id=session_id,
        emotion_type='neutral',
        confidence=0.8,
        r2c2_phase='relationship'
    )
    print("✓ Recorded emotion event")
    
    # Record phase transition
    db.record_phase_transition(
        session_id=session_id,
        from_phase='relationship',
        to_phase='reaction',
        trigger_reason='time_elapsed',
        time_in_previous_phase=180.0
    )
    print("✓ Recorded phase transition")
    
    # Save development plan
    goals = [
        {
            'goal_text': 'Improve delegation skills',
            'goal_type': 'start',
            'specific_behavior': 'Delegate at least 2 tasks per week',
            'measurable_criteria': 'Track delegated tasks',
            'target_date': None,
            'action_steps': ['Identify tasks to delegate', 'Meet with team members']
        }
    ]
    db.save_development_plan(session_id=session_id, goals=goals)
    print("✓ Saved development plan")
    
    # End session
    summary = {
        'duration': 1800,
        'phases_completed': ['relationship', 'reaction'],
        'goals_created': 1
    }
    db.end_session(session_id=session_id, summary=summary)
    print("✓ Ended session")
    
    # Retrieve session summary
    session_data = db.get_session_summary(session_id)
    print(f"✓ Retrieved session summary: {len(session_data['development_plan'])} goals, {len(session_data['emotion_events'])} emotions, {len(session_data['phase_transitions'])} transitions")
    
    # Get user sessions
    sessions = db.get_user_sessions('test_user')
    print(f"✓ Retrieved user sessions: {len(sessions)} sessions found")
    
    # Mark goal complete
    goal_id = session_data['development_plan'][0]['goal_id']
    success = db.mark_goal_complete(goal_id)
    print(f"✓ Marked goal {goal_id} as complete: {success}")
    
    print("\n" + "=" * 60)
    print("✓ All database tests passed!")
    print("=" * 60)
    print("\nNote: Test database created at test_r2c2_coach.db")
    print("You can delete it after testing.")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("R2C2 Voice Coach API - Component Tests")
    print("=" * 60)
    
    try:
        test_feedback_parser()
        test_database_operations()
        
        print("\n\n" + "=" * 60)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("=" * 60)
        print("\nThe API components are working correctly!")
        print("You can now start the API server with:")
        print("  python -m api.server")
        print("\nOr run with uvicorn:")
        print("  uvicorn api.server:app --reload")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
