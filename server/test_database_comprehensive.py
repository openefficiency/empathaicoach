"""Comprehensive database operation tests.

Tests session creation and retrieval, development plan saving,
emotion event recording, goal completion, and data integrity.
"""

import os
import tempfile
from datetime import datetime, timedelta
from database import SessionDatabase, initialize_database


def test_session_lifecycle():
    """Test complete session lifecycle from creation to completion."""
    print("\n" + "="*70)
    print("TEST: Session Lifecycle")
    print("="*70)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Initialize database
        print("\n1. Initializing database...")
        initialize_database(db_path)
        db = SessionDatabase(db_path)
        print("   ✓ Database initialized")
        
        # Create session
        print("\n2. Creating session...")
        feedback_data = {
            'feedback_id': 'fb-001',
            'themes': [
                {'category': 'improvement', 'theme': 'communication', 'frequency': 5},
                {'category': 'strength', 'theme': 'technical skills', 'frequency': 8}
            ],
            'comments': ['Great technical knowledge', 'Could improve communication']
        }
        session_id = db.create_session('user-123', feedback_data)
        assert session_id > 0
        print(f"   ✓ Created session ID: {session_id}")
        
        # Verify session exists
        session = db.get_session_by_id(session_id)
        assert session is not None
        assert session['user_id'] == 'user-123'
        assert session['end_time'] is None  # Session not ended yet
        print("   ✓ Session retrieved and verified")
        
        # End session
        print("\n3. Ending session...")
        summary = {
            'duration': 1800,
            'phases_completed': ['relationship', 'reaction', 'content', 'coaching'],
            'key_insights': ['Improved self-awareness', 'Clear action plan']
        }
        db.end_session(session_id, summary)
        
        # Verify session ended
        session = db.get_session_by_id(session_id)
        assert session['end_time'] is not None
        assert session['session_summary'] is not None
        print("   ✓ Session ended successfully")
        
        print("\n" + "="*70)
        print("✓ Session lifecycle test passed!")
        print("="*70)
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_development_plan_operations():
    """Test development plan creation, retrieval, and goal completion."""
    print("\n" + "="*70)
    print("TEST: Development Plan Operations")
    print("="*70)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        initialize_database(db_path)
        db = SessionDatabase(db_path)
        
        # Create session
        session_id = db.create_session('user-456', {'themes': []})
        
        # Save development plan with multiple goals
        print("\n1. Saving development plan...")
        goals = [
            {
                'goal_text': 'Improve delegation skills',
                'goal_type': 'start',
                'specific_behavior': 'Delegate at least one task per week',
                'measurable_criteria': 'Track delegated tasks in weekly log',
                'target_date': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
                'action_steps': ['Identify tasks to delegate', 'Schedule delegation meetings']
            },
            {
                'goal_text': 'Stop micromanaging',
                'goal_type': 'stop',
                'specific_behavior': 'Allow team members to complete tasks without constant check-ins',
                'measurable_criteria': 'Reduce check-ins to once per day',
                'target_date': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
                'action_steps': ['Set clear expectations upfront', 'Trust team members']
            },
            {
                'goal_text': 'Continue strong technical leadership',
                'goal_type': 'continue',
                'specific_behavior': 'Maintain weekly technical reviews',
                'measurable_criteria': 'Weekly review sessions held',
                'target_date': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
                'action_steps': ['Keep current schedule', 'Gather feedback']
            }
        ]
        
        db.save_development_plan(session_id, goals)
        print(f"   ✓ Saved {len(goals)} goals")
        
        # Retrieve and verify
        print("\n2. Retrieving development plan...")
        summary = db.get_session_summary(session_id)
        assert len(summary['development_plan']) == 3
        
        for i, goal in enumerate(summary['development_plan']):
            assert goal['goal_text'] == goals[i]['goal_text']
            assert goal['goal_type'] == goals[i]['goal_type']
            assert goal['is_completed'] == False
            print(f"   ✓ Goal {i+1}: {goal['goal_type']} - {goal['goal_text'][:40]}...")
        
        # Mark goals as complete
        print("\n3. Marking goals as complete...")
        goal_ids = [g['goal_id'] for g in summary['development_plan']]
        
        # Complete first two goals
        for i in range(2):
            success = db.mark_goal_complete(goal_ids[i])
            assert success
            print(f"   ✓ Marked goal {goal_ids[i]} as complete")
        
        # Verify completion status
        print("\n4. Verifying completion status...")
        updated_summary = db.get_session_summary(session_id)
        completed_count = sum(1 for g in updated_summary['development_plan'] if g['is_completed'])
        assert completed_count == 2
        print(f"   ✓ {completed_count} goals marked as complete")
        print(f"   ✓ {len(updated_summary['development_plan']) - completed_count} goals still pending")
        
        print("\n" + "="*70)
        print("✓ Development plan operations test passed!")
        print("="*70)
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_emotion_event_tracking():
    """Test emotion event recording and retrieval."""
    print("\n" + "="*70)
    print("TEST: Emotion Event Tracking")
    print("="*70)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        initialize_database(db_path)
        db = SessionDatabase(db_path)
        
        session_id = db.create_session('user-789', {'themes': []})
        
        # Record emotion events throughout session
        print("\n1. Recording emotion events...")
        emotions = [
            ('neutral', 0.85, 'relationship', {'pitch': 150.0, 'energy': 0.5}),
            ('defensive', 0.72, 'reaction', {'pitch': 180.0, 'energy': 0.8}),
            ('frustrated', 0.68, 'reaction', {'pitch': 175.0, 'energy': 0.85}),
            ('neutral', 0.80, 'reaction', {'pitch': 155.0, 'energy': 0.6}),
            ('positive', 0.75, 'content', {'pitch': 160.0, 'energy': 0.65}),
            ('positive', 0.82, 'coaching', {'pitch': 165.0, 'energy': 0.7})
        ]
        
        for emotion_type, confidence, phase, features in emotions:
            db.record_emotion_event(
                session_id=session_id,
                emotion_type=emotion_type,
                confidence=confidence,
                r2c2_phase=phase,
                audio_features=features
            )
        
        print(f"   ✓ Recorded {len(emotions)} emotion events")
        
        # Retrieve and analyze
        print("\n2. Analyzing emotion events...")
        summary = db.get_session_summary(session_id)
        emotion_events = summary['emotion_events']
        
        assert len(emotion_events) == len(emotions)
        
        # Count emotions by type
        emotion_counts = {}
        for event in emotion_events:
            emotion = event['emotion_type']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        print("   Emotion distribution:")
        for emotion, count in emotion_counts.items():
            print(f"     - {emotion}: {count} occurrences")
        
        # Verify emotional journey
        first_emotion = emotion_events[0]['emotion_type']
        last_emotion = emotion_events[-1]['emotion_type']
        print(f"\n   ✓ Emotional journey: {first_emotion} → {last_emotion}")
        
        # Verify audio features are stored
        assert 'audio_features' in emotion_events[0]
        print("   ✓ Audio features stored with events")
        
        print("\n" + "="*70)
        print("✓ Emotion event tracking test passed!")
        print("="*70)
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_phase_transition_tracking():
    """Test phase transition recording and analysis."""
    print("\n" + "="*70)
    print("TEST: Phase Transition Tracking")
    print("="*70)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        initialize_database(db_path)
        db = SessionDatabase(db_path)
        
        session_id = db.create_session('user-101', {'themes': []})
        
        # Record phase transitions
        print("\n1. Recording phase transitions...")
        transitions = [
            ('relationship', 'reaction', 'Time threshold reached', 145.5),
            ('reaction', 'content', 'Emotional readiness detected', 210.3),
            ('content', 'coaching', 'Key themes discussed', 280.7)
        ]
        
        for from_phase, to_phase, reason, duration in transitions:
            db.record_phase_transition(
                session_id=session_id,
                from_phase=from_phase,
                to_phase=to_phase,
                trigger_reason=reason,
                time_in_previous_phase=duration
            )
        
        print(f"   ✓ Recorded {len(transitions)} phase transitions")
        
        # Retrieve and analyze
        print("\n2. Analyzing phase transitions...")
        summary = db.get_session_summary(session_id)
        phase_transitions = summary['phase_transitions']
        
        assert len(phase_transitions) == len(transitions)
        
        total_time = 0
        for i, transition in enumerate(phase_transitions):
            from_phase = transition['from_phase']
            to_phase = transition['to_phase']
            duration = transition['time_in_previous_phase']
            reason = transition['trigger_reason']
            
            total_time += duration
            
            print(f"   Transition {i+1}:")
            print(f"     {from_phase} → {to_phase}")
            print(f"     Duration: {duration:.1f}s")
            print(f"     Reason: {reason}")
        
        print(f"\n   ✓ Total session time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        
        print("\n" + "="*70)
        print("✓ Phase transition tracking test passed!")
        print("="*70)
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_multi_user_sessions():
    """Test multiple users with multiple sessions."""
    print("\n" + "="*70)
    print("TEST: Multi-User Sessions")
    print("="*70)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        initialize_database(db_path)
        db = SessionDatabase(db_path)
        
        # Create sessions for multiple users
        print("\n1. Creating sessions for multiple users...")
        users = ['alice', 'bob', 'charlie']
        user_sessions = {}
        
        for user in users:
            user_sessions[user] = []
            # Create 2-3 sessions per user
            num_sessions = 2 if user == 'alice' else 3
            
            for i in range(num_sessions):
                session_id = db.create_session(
                    user_id=user,
                    feedback_data={'themes': [f'theme-{i}']}
                )
                user_sessions[user].append(session_id)
            
            print(f"   ✓ Created {num_sessions} sessions for {user}")
        
        # Retrieve sessions by user
        print("\n2. Retrieving sessions by user...")
        for user in users:
            sessions = db.get_user_sessions(user)
            expected_count = len(user_sessions[user])
            assert len(sessions) == expected_count
            print(f"   ✓ {user}: {len(sessions)} sessions retrieved")
        
        # Verify session isolation
        print("\n3. Verifying session isolation...")
        alice_sessions = db.get_user_sessions('alice')
        bob_sessions = db.get_user_sessions('bob')
        
        alice_ids = {s['session_id'] for s in alice_sessions}
        bob_ids = {s['session_id'] for s in bob_sessions}
        
        assert len(alice_ids.intersection(bob_ids)) == 0
        print("   ✓ User sessions are properly isolated")
        
        print("\n" + "="*70)
        print("✓ Multi-user sessions test passed!")
        print("="*70)
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_data_integrity():
    """Test data integrity constraints and error handling."""
    print("\n" + "="*70)
    print("TEST: Data Integrity")
    print("="*70)
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        initialize_database(db_path)
        db = SessionDatabase(db_path)
        
        # Test 1: Cannot retrieve non-existent session
        print("\n1. Testing non-existent session retrieval...")
        session = db.get_session_by_id(99999)
        assert session is None
        print("   ✓ Non-existent session returns None")
        
        # Test 2: Cannot complete non-existent goal
        print("\n2. Testing non-existent goal completion...")
        success = db.mark_goal_complete(99999)
        assert not success
        print("   ✓ Non-existent goal completion returns False")
        
        # Test 3: Session summary with no data
        print("\n3. Testing session summary with minimal data...")
        session_id = db.create_session('user-test', {'themes': []})
        summary = db.get_session_summary(session_id)
        
        assert summary is not None
        assert summary['session_id'] == session_id
        assert len(summary['development_plan']) == 0
        assert len(summary['emotion_events']) == 0
        assert len(summary['phase_transitions']) == 0
        print("   ✓ Empty session summary handled correctly")
        
        # Test 4: Large feedback data
        print("\n4. Testing large feedback data...")
        large_feedback = {
            'themes': [{'theme': f'theme-{i}', 'frequency': i} for i in range(50)],
            'comments': [f'Comment {i}' * 100 for i in range(100)]
        }
        session_id = db.create_session('user-large', large_feedback)
        retrieved = db.get_session_by_id(session_id)
        assert retrieved is not None
        print("   ✓ Large feedback data stored and retrieved")
        
        print("\n" + "="*70)
        print("✓ Data integrity test passed!")
        print("="*70)
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def run_all_tests():
    """Run all database tests."""
    print("\n" + "="*70)
    print("DATABASE OPERATIONS TEST SUITE")
    print("="*70)
    print("\nTesting Requirements:")
    print("- 13.1: Session creation and retrieval")
    print("- 13.2: Development plan saving")
    print("- 13.3: Emotion event recording")
    print("- 13.4: Goal completion")
    print("- 13.5: Data integrity")
    print("- 13.6: Multi-user support")
    print("="*70)
    
    try:
        test_session_lifecycle()
        test_development_plan_operations()
        test_emotion_event_tracking()
        test_phase_transition_tracking()
        test_multi_user_sessions()
        test_data_integrity()
        
        print("\n" + "="*70)
        print("✓✓✓ ALL DATABASE TESTS PASSED ✓✓✓")
        print("="*70)
        print("\nSummary:")
        print("✓ Session lifecycle management works correctly")
        print("✓ Development plan operations function properly")
        print("✓ Emotion event tracking is accurate")
        print("✓ Phase transition tracking works as expected")
        print("✓ Multi-user sessions are properly isolated")
        print("✓ Data integrity is maintained")
        print("\nThe database system is working correctly!")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
