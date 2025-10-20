"""End-to-end integration tests for R2C2 Voice Coach.

Tests complete R2C2 session flow from start to finish,
including all components working together.
"""

import os
import tempfile
import numpy as np
from datetime import datetime
from r2c2 import R2C2Engine, R2C2Phase, FeedbackData, EmotionState
from r2c2.emotion_detector import EmotionDetector, EmotionType
from database import SessionDatabase, initialize_database


def create_sample_feedback():
    """Create sample 360° feedback data."""
    return FeedbackData(
        feedback_id="e2e-test-001",
        user_id="test-user-e2e",
        collection_date=datetime.now(),
        themes=[
            {
                'category': 'improvement',
                'theme': 'communication clarity',
                'frequency': 5,
                'examples': [
                    'Could be more clear in emails',
                    'Sometimes hard to understand in meetings',
                    'Needs to check for understanding more often'
                ]
            },
            {
                'category': 'improvement',
                'theme': 'delegation',
                'frequency': 4,
                'examples': [
                    'Tends to do too much themselves',
                    'Could empower team more',
                    'Needs to trust team members'
                ]
            },
            {
                'category': 'strength',
                'theme': 'technical expertise',
                'frequency': 8,
                'examples': [
                    'Very knowledgeable',
                    'Great problem solver',
                    'Go-to person for technical questions'
                ]
            },
            {
                'category': 'strength',
                'theme': 'work ethic',
                'frequency': 6,
                'examples': [
                    'Always delivers on time',
                    'Very reliable',
                    'Dedicated to quality'
                ]
            }
        ],
        raw_comments=[
            {
                'source': 'manager',
                'category': 'communication',
                'comment': 'Could be more clear in written communication',
                'sentiment': 'negative'
            },
            {
                'source': 'peer',
                'category': 'technical',
                'comment': 'Excellent technical skills',
                'sentiment': 'positive'
            },
            {
                'source': 'direct_report',
                'category': 'delegation',
                'comment': 'Would like more autonomy',
                'sentiment': 'negative'
            }
        ]
    )


def simulate_user_responses():
    """Simulate user responses throughout the session."""
    return {
        'relationship': [
            "I'm feeling a bit nervous about this feedback.",
            "I've read through it, and some parts were hard to hear.",
            "I'm ready to talk about it though."
        ],
        'reaction': [
            "The comments about my communication really surprised me.",
            "I feel like I'm being misunderstood - I try so hard to be clear!",
            "Maybe I'm being defensive... I guess I do feel hurt by some of this.",
            "Okay, I can see that my initial reaction was pretty strong.",
            "I'm starting to feel more calm about it now."
        ],
        'content': [
            "Looking at the patterns, communication and delegation come up a lot.",
            "I think the communication issue might be about checking for understanding.",
            "The delegation feedback makes sense - I do tend to do things myself.",
            "I can see how my behavior might impact my team's growth."
        ],
        'coaching': [
            "I want to focus on communication and delegation.",
            "For communication, I'll start sending summary emails after meetings.",
            "For delegation, I'll identify one task per week to delegate.",
            "I'll track my progress in a weekly log.",
            "I think I can start this next week."
        ]
    }


def test_complete_r2c2_session():
    """Test a complete R2C2 session from start to finish."""
    print("\n" + "="*70)
    print("TEST: Complete R2C2 Session Flow")
    print("="*70)
    
    # Setup
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Initialize components
        print("\n1. Initializing components...")
        initialize_database(db_path)
        db = SessionDatabase(db_path)
        
        feedback = create_sample_feedback()
        r2c2_engine = R2C2Engine(feedback)
        emotion_detector = EmotionDetector()
        
        print("   ✓ Database initialized")
        print("   ✓ R2C2 engine created")
        print("   ✓ Emotion detector ready")
        
        # Create session in database
        session_id = db.create_session(feedback.user_id, {
            'feedback_id': feedback.feedback_id,
            'themes': feedback.themes
        })
        print(f"   ✓ Session created: ID {session_id}")
        
        # Simulate session flow
        user_responses = simulate_user_responses()
        
        # Phase 1: Relationship Building
        print("\n2. RELATIONSHIP BUILDING PHASE")
        print("   " + "-"*66)
        assert r2c2_engine.get_current_phase() == R2C2Phase.RELATIONSHIP
        
        for i, response in enumerate(user_responses['relationship']):
            # Simulate neutral/slightly anxious emotions
            emotion = EmotionState(
                emotion='anxious' if i == 0 else 'neutral',
                confidence=0.75,
                timestamp=datetime.now()
            )
            
            r2c2_engine.record_user_response(response, emotion)
            db.record_emotion_event(
                session_id=session_id,
                emotion_type=emotion.emotion,
                confidence=emotion.confidence,
                r2c2_phase='relationship'
            )
            
            print(f"   User: {response[:60]}...")
            print(f"   Emotion: {emotion.emotion} ({emotion.confidence:.2f})")
        
        # Transition to Reaction
        r2c2_engine.state.phase_start_time = datetime.now()
        from datetime import timedelta
        r2c2_engine.state.phase_start_time -= timedelta(seconds=130)
        
        assert r2c2_engine.should_transition()
        new_phase = r2c2_engine.transition_to_next_phase()
        db.record_phase_transition(
            session_id=session_id,
            from_phase='relationship',
            to_phase='reaction',
            trigger_reason='Time threshold reached',
            time_in_previous_phase=130.0
        )
        print(f"   ✓ Transitioned to {new_phase.value} phase")
        
        # Phase 2: Reaction Exploration
        print("\n3. REACTION EXPLORATION PHASE")
        print("   " + "-"*66)
        
        for i, response in enumerate(user_responses['reaction']):
            # Simulate emotional journey: defensive → frustrated → neutral
            if i < 2:
                emotion_type = 'defensive'
            elif i < 3:
                emotion_type = 'frustrated'
            else:
                emotion_type = 'neutral'
            
            emotion = EmotionState(
                emotion=emotion_type,
                confidence=0.70 + (i * 0.02),
                timestamp=datetime.now()
            )
            
            r2c2_engine.record_user_response(response, emotion)
            db.record_emotion_event(
                session_id=session_id,
                emotion_type=emotion.emotion,
                confidence=emotion.confidence,
                r2c2_phase='reaction'
            )
            
            print(f"   User: {response[:60]}...")
            print(f"   Emotion: {emotion.emotion} ({emotion.confidence:.2f})")
        
        # Transition to Content
        r2c2_engine.state.phase_start_time -= timedelta(seconds=200)
        assert r2c2_engine.should_transition()
        new_phase = r2c2_engine.transition_to_next_phase()
        db.record_phase_transition(
            session_id=session_id,
            from_phase='reaction',
            to_phase='content',
            trigger_reason='Emotional readiness detected',
            time_in_previous_phase=200.0
        )
        print(f"   ✓ Transitioned to {new_phase.value} phase")
        
        # Phase 3: Content Discussion
        print("\n4. CONTENT DISCUSSION PHASE")
        print("   " + "-"*66)
        
        for i, response in enumerate(user_responses['content']):
            emotion = EmotionState(
                emotion='neutral' if i < 3 else 'positive',
                confidence=0.78,
                timestamp=datetime.now()
            )
            
            r2c2_engine.record_user_response(response, emotion)
            db.record_emotion_event(
                session_id=session_id,
                emotion_type=emotion.emotion,
                confidence=emotion.confidence,
                r2c2_phase='content'
            )
            
            print(f"   User: {response[:60]}...")
            print(f"   Emotion: {emotion.emotion} ({emotion.confidence:.2f})")
        
        # Verify content themes were extracted
        assert len(r2c2_engine.state.content_themes) >= 2
        print(f"   ✓ Identified themes: {', '.join(r2c2_engine.state.content_themes)}")
        
        # Transition to Coaching
        r2c2_engine.state.phase_start_time -= timedelta(seconds=250)
        assert r2c2_engine.should_transition()
        new_phase = r2c2_engine.transition_to_next_phase()
        db.record_phase_transition(
            session_id=session_id,
            from_phase='content',
            to_phase='coaching',
            trigger_reason='Key themes discussed',
            time_in_previous_phase=250.0
        )
        print(f"   ✓ Transitioned to {new_phase.value} phase")
        
        # Phase 4: Coaching for Change
        print("\n5. COACHING FOR CHANGE PHASE")
        print("   " + "-"*66)
        
        for i, response in enumerate(user_responses['coaching']):
            emotion = EmotionState(
                emotion='positive',
                confidence=0.82,
                timestamp=datetime.now()
            )
            
            r2c2_engine.record_user_response(response, emotion)
            db.record_emotion_event(
                session_id=session_id,
                emotion_type=emotion.emotion,
                confidence=emotion.confidence,
                r2c2_phase='coaching'
            )
            
            print(f"   User: {response[:60]}...")
            print(f"   Emotion: {emotion.emotion} ({emotion.confidence:.2f})")
        
        # Verify development plan was created
        assert r2c2_engine.state.development_plan is not None
        assert len(r2c2_engine.state.development_plan.goals) >= 2
        print(f"   ✓ Development plan created with {len(r2c2_engine.state.development_plan.goals)} goals")
        
        # Save development plan to database
        goals = [
            {
                'goal_text': 'Improve communication clarity',
                'goal_type': 'start',
                'specific_behavior': 'Send summary email after each meeting',
                'measurable_criteria': 'Summary emails sent within 24 hours',
                'target_date': None,
                'action_steps': ['Create email template', 'Set calendar reminder']
            },
            {
                'goal_text': 'Delegate more effectively',
                'goal_type': 'start',
                'specific_behavior': 'Delegate one task per week',
                'measurable_criteria': 'Track delegated tasks in weekly log',
                'target_date': None,
                'action_steps': ['Identify tasks to delegate', 'Meet with team members']
            }
        ]
        db.save_development_plan(session_id, goals)
        print("   ✓ Development plan saved to database")
        
        # End session
        print("\n6. ENDING SESSION")
        print("   " + "-"*66)
        
        summary = r2c2_engine.get_session_summary()
        db.end_session(session_id, summary)
        
        print(f"   Session duration: {summary['duration_seconds']:.1f}s")
        print(f"   Phases completed: {', '.join(summary['phases_completed'])}")
        print(f"   Emotional journey: {summary['emotional_journey']['start_emotion']} → {summary['emotional_journey']['end_emotion']}")
        print(f"   Development plan: {summary['development_plan']['goal_count']} goals")
        print("   ✓ Session ended successfully")
        
        # Verify complete session data
        print("\n7. VERIFYING SESSION DATA")
        print("   " + "-"*66)
        
        session_data = db.get_session_summary(session_id)
        
        assert session_data is not None
        assert len(session_data['emotion_events']) > 0
        assert len(session_data['phase_transitions']) == 3
        assert len(session_data['development_plan']) == 2
        
        print(f"   ✓ Emotion events: {len(session_data['emotion_events'])}")
        print(f"   ✓ Phase transitions: {len(session_data['phase_transitions'])}")
        print(f"   ✓ Development plan goals: {len(session_data['development_plan'])}")
        
        # Verify emotional progression
        emotions = [e['emotion_type'] for e in session_data['emotion_events']]
        print(f"   ✓ Emotional progression: {' → '.join(emotions[:3])} ... {' → '.join(emotions[-3:])}")
        
        print("\n" + "="*70)
        print("✓ Complete R2C2 session flow test passed!")
        print("="*70)
        
        return True
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_error_scenarios():
    """Test error handling scenarios."""
    print("\n" + "="*70)
    print("TEST: Error Scenarios")
    print("="*70)
    
    # Test 1: Session with minimal feedback
    print("\n1. Testing session with minimal feedback...")
    feedback = FeedbackData(
        feedback_id="minimal-001",
        user_id="user-minimal",
        collection_date=datetime.now(),
        themes=[],
        raw_comments=[]
    )
    
    engine = R2C2Engine(feedback)
    assert engine.get_current_phase() == R2C2Phase.RELATIONSHIP
    
    # Should still generate prompts
    prompt = engine.get_phase_prompt()
    assert len(prompt) > 0
    print("   ✓ Engine handles minimal feedback gracefully")
    
    # Test 2: Empty user responses
    print("\n2. Testing empty user responses...")
    engine.record_user_response("", None)
    engine.record_user_response("   ", None)
    # Should not crash
    print("   ✓ Empty responses handled gracefully")
    
    # Test 3: Rapid phase transitions
    print("\n3. Testing rapid phase transitions...")
    for _ in range(5):
        engine.transition_to_next_phase()
    # Should stay in final phase
    assert engine.get_current_phase() == R2C2Phase.COACHING
    print("   ✓ Rapid transitions handled correctly")
    
    # Test 4: Emotion detector with no history
    print("\n4. Testing emotion detector with no history...")
    detector = EmotionDetector()
    trend = detector.get_emotion_trend()
    assert trend == EmotionType.NEUTRAL
    is_ready = detector.is_emotionally_ready_for_transition()
    assert not is_ready
    print("   ✓ Emotion detector handles empty history")
    
    print("\n" + "="*70)
    print("✓ Error scenarios test passed!")
    print("="*70)


def test_session_with_sample_feedback():
    """Test session with realistic sample feedback."""
    print("\n" + "="*70)
    print("TEST: Session with Sample Feedback")
    print("="*70)
    
    # Load sample feedback if available
    sample_feedback_path = "../sample-feedback/sample_feedback.json"
    
    if os.path.exists(sample_feedback_path):
        print("\n1. Loading sample feedback file...")
        import json
        with open(sample_feedback_path, 'r') as f:
            feedback_json = json.load(f)
        
        feedback = FeedbackData(
            feedback_id=feedback_json.get('feedback_id', 'sample-001'),
            user_id=feedback_json.get('user_id', 'sample-user'),
            collection_date=datetime.now(),
            themes=feedback_json.get('themes', []),
            raw_comments=feedback_json.get('comments', [])
        )
        print(f"   ✓ Loaded feedback with {len(feedback.themes)} themes")
    else:
        print("\n1. Using generated sample feedback...")
        feedback = create_sample_feedback()
        print(f"   ✓ Created feedback with {len(feedback.themes)} themes")
    
    # Create engine and verify it works
    print("\n2. Testing engine with sample feedback...")
    engine = R2C2Engine(feedback)
    
    # Get prompts for each phase
    for phase in [R2C2Phase.RELATIONSHIP, R2C2Phase.REACTION, R2C2Phase.CONTENT, R2C2Phase.COACHING]:
        engine.state.current_phase = phase
        prompt = engine.get_phase_prompt()
        assert len(prompt) > 0
        print(f"   ✓ {phase.value} phase prompt generated ({len(prompt)} chars)")
    
    print("\n" + "="*70)
    print("✓ Sample feedback test passed!")
    print("="*70)


def run_all_tests():
    """Run all end-to-end tests."""
    print("\n" + "="*70)
    print("END-TO-END INTEGRATION TEST SUITE")
    print("="*70)
    print("\nTesting Requirements:")
    print("- 1.1-1.5: Complete R2C2 session flow")
    print("- 16.1-16.7: Error handling and recovery")
    print("="*70)
    
    try:
        test_complete_r2c2_session()
        test_error_scenarios()
        test_session_with_sample_feedback()
        
        print("\n" + "="*70)
        print("✓✓✓ ALL END-TO-END TESTS PASSED ✓✓✓")
        print("="*70)
        print("\nSummary:")
        print("✓ Complete R2C2 session flow works correctly")
        print("✓ All components integrate properly")
        print("✓ Error scenarios are handled gracefully")
        print("✓ Sample feedback processing works")
        print("\nThe R2C2 Voice Coach system is working end-to-end!")
        
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
