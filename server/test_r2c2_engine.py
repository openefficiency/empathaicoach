"""Simple test script to verify R2C2 engine functionality."""

from datetime import datetime
from r2c2 import R2C2Engine, R2C2Phase, FeedbackData, EmotionState

def test_r2c2_engine():
    """Test basic R2C2 engine functionality."""
    
    print("Testing R2C2 Engine Implementation\n")
    print("=" * 50)
    
    # Create sample feedback data
    feedback = FeedbackData(
        feedback_id="test-001",
        user_id="user-123",
        collection_date=datetime.now(),
        themes=[
            {
                'category': 'improvement',
                'theme': 'communication clarity',
                'frequency': 5,
                'examples': ['Could be more clear in emails']
            },
            {
                'category': 'strength',
                'theme': 'technical expertise',
                'frequency': 8,
                'examples': ['Very knowledgeable']
            }
        ]
    )
    
    # Initialize engine
    print("\n1. Initializing R2C2 Engine...")
    engine = R2C2Engine(feedback)
    print(f"   ✓ Engine initialized in {engine.get_current_phase().value} phase")
    
    # Test phase prompt generation
    print("\n2. Testing phase prompt generation...")
    prompt = engine.get_phase_prompt()
    print(f"   ✓ Generated prompt ({len(prompt)} characters)")
    print(f"   Preview: {prompt[:100]}...")
    
    # Test phase guidance
    print("\n3. Testing phase guidance...")
    guidance = engine.get_phase_guidance()
    print(f"   ✓ Phase: {guidance['phase']}")
    print(f"   ✓ Goals: {len(guidance['goals'])} goals")
    print(f"   ✓ Key questions: {len(guidance['key_questions'])} questions")
    
    # Test recording user response
    print("\n4. Testing user response recording...")
    emotion = EmotionState(
        emotion='neutral',
        confidence=0.8,
        timestamp=datetime.now()
    )
    engine.record_user_response("I feel a bit nervous about this feedback", emotion)
    print(f"   ✓ Recorded response with emotion: {emotion.emotion}")
    
    # Test phase transition logic
    print("\n5. Testing phase transition logic...")
    should_transition = engine.should_transition()
    print(f"   ✓ Should transition: {should_transition}")
    print(f"   ✓ Time in phase: {engine.get_time_in_phase():.2f} seconds")
    
    # Force transition to next phase
    print("\n6. Testing manual phase transition...")
    old_phase = engine.get_current_phase()
    new_phase = engine.transition_to_next_phase()
    print(f"   ✓ Transitioned from {old_phase.value} to {new_phase.value}")
    
    # Test new phase prompt
    print("\n7. Testing new phase prompt...")
    new_prompt = engine.get_phase_prompt()
    print(f"   ✓ Generated new prompt for {new_phase.value} phase")
    print(f"   Preview: {new_prompt[:100]}...")
    
    # Test session summary
    print("\n8. Testing session summary generation...")
    summary = engine.get_session_summary()
    print(f"   ✓ Session duration: {summary['duration_seconds']:.2f} seconds")
    print(f"   ✓ Phases completed: {len(summary['phases_completed'])}")
    print(f"   ✓ Current phase: {summary['current_phase']}")
    print(f"   ✓ Emotional journey: {summary['emotional_journey']['start_emotion']} → {summary['emotional_journey']['end_emotion']}")
    
    # Test state management
    print("\n9. Testing state management...")
    state = engine.get_state()
    print(f"   ✓ Retrieved state with {len(state.emotional_states)} emotion records")
    print(f"   ✓ Phase history: {len(state.phase_history)} transitions")
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("\nR2C2 Engine is ready for integration.")

if __name__ == "__main__":
    test_r2c2_engine()
