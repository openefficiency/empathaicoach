"""Comprehensive tests for R2C2 phase transitions.

Tests automatic transitions based on time, emotion-based transitions,
manual phase progression, and phase prompt correctness.
"""

import time
from datetime import datetime, timedelta
from r2c2 import R2C2Engine, R2C2Phase, FeedbackData, EmotionState


def test_automatic_time_based_transitions():
    """Test automatic phase transitions based on time thresholds."""
    print("\n" + "="*70)
    print("TEST: Automatic Time-Based Phase Transitions")
    print("="*70)
    
    # Create feedback data
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
            }
        ]
    )
    
    engine = R2C2Engine(feedback)
    
    # Test 1: Relationship phase - should not transition immediately
    print("\n1. Testing Relationship phase minimum duration...")
    assert engine.get_current_phase() == R2C2Phase.RELATIONSHIP
    assert not engine.should_transition(), "Should not transition immediately"
    print("   ✓ Relationship phase requires minimum time")
    
    # Simulate time passing by manipulating phase start time
    engine.state.phase_start_time = datetime.now() - timedelta(seconds=130)
    assert engine.should_transition(), "Should transition after 2+ minutes"
    print("   ✓ Transitions after minimum duration (120s)")
    
    # Test 2: Transition to Reaction phase
    print("\n2. Testing transition to Reaction phase...")
    new_phase = engine.transition_to_next_phase()
    assert new_phase == R2C2Phase.REACTION
    assert engine.get_current_phase() == R2C2Phase.REACTION
    print("   ✓ Successfully transitioned to Reaction phase")
    
    # Test 3: Reaction phase - requires emotional readiness
    print("\n3. Testing Reaction phase transition logic...")
    engine.state.phase_start_time = datetime.now() - timedelta(seconds=200)
    
    # Add defensive emotions - should not transition yet
    for i in range(3):
        emotion = EmotionState(
            emotion='defensive',
            confidence=0.8,
            timestamp=datetime.now() - timedelta(seconds=60-i*10)
        )
        engine.state.emotional_states.append(emotion)
    
    assert not engine.should_transition(), "Should not transition with defensive emotions"
    print("   ✓ Reaction phase waits for emotional readiness")
    
    # Add neutral emotions - should now transition
    for i in range(3):
        emotion = EmotionState(
            emotion='neutral',
            confidence=0.8,
            timestamp=datetime.now() - timedelta(seconds=i)
        )
        engine.state.emotional_states.append(emotion)
    
    assert engine.should_transition(), "Should transition with neutral emotions"
    print("   ✓ Transitions when emotions become neutral/positive")
    
    # Test 4: Transition to Content phase
    print("\n4. Testing transition to Content phase...")
    new_phase = engine.transition_to_next_phase()
    assert new_phase == R2C2Phase.CONTENT
    assert engine.get_current_phase() == R2C2Phase.CONTENT
    print("   ✓ Successfully transitioned to Content phase")
    
    # Test 5: Content phase - requires themes discussed
    print("\n5. Testing Content phase transition logic...")
    engine.state.phase_start_time = datetime.now() - timedelta(seconds=250)
    
    # Without content themes, should not transition
    assert not engine.should_transition(), "Should not transition without content themes"
    print("   ✓ Content phase requires discussion of themes")
    
    # Add content themes
    engine.state.content_themes = ['communication', 'leadership', 'delegation']
    assert engine.should_transition(), "Should transition with themes discussed"
    print("   ✓ Transitions when key themes are discussed")
    
    # Test 6: Transition to Coaching phase
    print("\n6. Testing transition to Coaching phase...")
    new_phase = engine.transition_to_next_phase()
    assert new_phase == R2C2Phase.COACHING
    assert engine.get_current_phase() == R2C2Phase.COACHING
    print("   ✓ Successfully transitioned to Coaching phase")
    
    # Test 7: Coaching phase - final phase, no auto-transition
    print("\n7. Testing Coaching phase (final phase)...")
    engine.state.phase_start_time = datetime.now() - timedelta(seconds=300)
    assert not engine.should_transition(), "Coaching phase should not auto-transition"
    
    # Try to transition - should stay in coaching
    new_phase = engine.transition_to_next_phase()
    assert new_phase == R2C2Phase.COACHING
    print("   ✓ Coaching phase is final, no further transitions")
    
    print("\n" + "="*70)
    print("✓ All automatic time-based transition tests passed!")
    print("="*70)


def test_emotion_based_transitions():
    """Test phase transitions triggered by emotional state changes."""
    print("\n" + "="*70)
    print("TEST: Emotion-Based Phase Transitions")
    print("="*70)
    
    feedback = FeedbackData(
        feedback_id="test-002",
        user_id="user-456",
        collection_date=datetime.now(),
        themes=[{'category': 'improvement', 'theme': 'delegation', 'frequency': 3}]
    )
    
    engine = R2C2Engine(feedback)
    
    # Test 1: Early transition with emotional readiness
    print("\n1. Testing early transition from Relationship with readiness...")
    engine.state.phase_start_time = datetime.now() - timedelta(seconds=95)
    
    # Add positive emotions indicating readiness
    for i in range(4):
        emotion = EmotionState(
            emotion='positive' if i % 2 == 0 else 'neutral',
            confidence=0.85,
            timestamp=datetime.now() - timedelta(seconds=60-i*15)
        )
        engine.state.emotional_states.append(emotion)
    
    assert engine.should_transition(), "Should allow early transition with emotional readiness"
    print("   ✓ Can transition early (90s+) with positive emotions")
    
    # Test 2: Defensive emotions prevent transition
    print("\n2. Testing that defensive emotions prevent transition...")
    engine.transition_to_next_phase()  # Move to Reaction
    engine.state.phase_start_time = datetime.now() - timedelta(seconds=200)
    
    # Clear previous emotions and add defensive ones
    engine.state.emotional_states.clear()
    for i in range(5):
        emotion = EmotionState(
            emotion='defensive',
            confidence=0.75,
            timestamp=datetime.now() - timedelta(seconds=60-i*10)
        )
        engine.state.emotional_states.append(emotion)
    
    assert not engine.should_transition(), "Defensive emotions should prevent transition"
    print("   ✓ Defensive emotions block transition from Reaction phase")
    
    # Test 3: Emotional shift enables transition
    print("\n3. Testing emotional shift from defensive to neutral...")
    
    # Add neutral emotions showing emotional processing
    for i in range(4):
        emotion = EmotionState(
            emotion='neutral',
            confidence=0.8,
            timestamp=datetime.now() - timedelta(seconds=i*5)
        )
        engine.state.emotional_states.append(emotion)
    
    assert engine.should_transition(), "Neutral emotions should enable transition"
    print("   ✓ Shift to neutral emotions enables transition")
    
    # Test 4: Frustrated emotions also prevent transition
    print("\n4. Testing frustrated emotions...")
    engine.state.emotional_states.clear()
    engine.state.phase_start_time = datetime.now() - timedelta(seconds=200)
    
    for i in range(4):
        emotion = EmotionState(
            emotion='frustrated',
            confidence=0.7,
            timestamp=datetime.now() - timedelta(seconds=60-i*15)
        )
        engine.state.emotional_states.append(emotion)
    
    assert not engine.should_transition(), "Frustrated emotions should prevent transition"
    print("   ✓ Frustrated emotions also block transition")
    
    # Test 5: Anxious emotions prevent transition
    print("\n5. Testing anxious emotions...")
    engine.state.emotional_states.clear()
    
    for i in range(4):
        emotion = EmotionState(
            emotion='anxious',
            confidence=0.75,
            timestamp=datetime.now() - timedelta(seconds=60-i*15)
        )
        engine.state.emotional_states.append(emotion)
    
    assert not engine.should_transition(), "Anxious emotions should prevent transition"
    print("   ✓ Anxious emotions block transition")
    
    # Test 6: Extended time overrides emotional state
    print("\n6. Testing extended time override...")
    engine.state.phase_start_time = datetime.now() - timedelta(seconds=650)
    
    assert engine.should_transition(), "Extended time should override emotional blocks"
    print("   ✓ After 10+ minutes, transition occurs regardless of emotions")
    
    print("\n" + "="*70)
    print("✓ All emotion-based transition tests passed!")
    print("="*70)


def test_manual_phase_progression():
    """Test manual phase transitions and phase history tracking."""
    print("\n" + "="*70)
    print("TEST: Manual Phase Progression")
    print("="*70)
    
    feedback = FeedbackData(
        feedback_id="test-003",
        user_id="user-789",
        collection_date=datetime.now(),
        themes=[{'category': 'strength', 'theme': 'technical skills', 'frequency': 7}]
    )
    
    engine = R2C2Engine(feedback)
    
    # Test 1: Manual transition through all phases
    print("\n1. Testing manual progression through all phases...")
    
    phases = [R2C2Phase.RELATIONSHIP, R2C2Phase.REACTION, R2C2Phase.CONTENT, R2C2Phase.COACHING]
    
    for i, expected_phase in enumerate(phases):
        current = engine.get_current_phase()
        assert current == expected_phase, f"Expected {expected_phase}, got {current}"
        print(f"   ✓ Currently in {current.value} phase")
        
        if i < len(phases) - 1:
            # Wait a bit to simulate time in phase
            time.sleep(0.1)
            next_phase = engine.transition_to_next_phase()
            print(f"   → Transitioned to {next_phase.value} phase")
    
    # Test 2: Phase history tracking
    print("\n2. Testing phase history tracking...")
    assert len(engine.state.phase_history) == 3, "Should have 3 completed phases"
    
    for i, phase_record in enumerate(engine.state.phase_history):
        expected_phases = ['relationship', 'reaction', 'content']
        assert phase_record['phase'] == expected_phases[i]
        assert 'duration' in phase_record
        assert 'ended_at' in phase_record
        print(f"   ✓ Phase {i+1}: {phase_record['phase']} - {phase_record['duration']:.2f}s")
    
    # Test 3: Time in phase tracking
    print("\n3. Testing time in phase tracking...")
    time.sleep(0.2)
    time_in_phase = engine.get_time_in_phase()
    assert time_in_phase >= 0.2, "Time in phase should be at least 0.2s"
    print(f"   ✓ Time in current phase: {time_in_phase:.2f}s")
    
    # Test 4: Cannot progress beyond final phase
    print("\n4. Testing final phase boundary...")
    assert engine.get_current_phase() == R2C2Phase.COACHING
    next_phase = engine.transition_to_next_phase()
    assert next_phase == R2C2Phase.COACHING, "Should remain in Coaching phase"
    print("   ✓ Cannot progress beyond Coaching phase")
    
    print("\n" + "="*70)
    print("✓ All manual phase progression tests passed!")
    print("="*70)


def test_phase_prompts_correctness():
    """Test that phase prompts are correct and contain expected content."""
    print("\n" + "="*70)
    print("TEST: Phase Prompt Correctness")
    print("="*70)
    
    feedback = FeedbackData(
        feedback_id="test-004",
        user_id="user-101",
        collection_date=datetime.now(),
        themes=[
            {'category': 'improvement', 'theme': 'time management', 'frequency': 4},
            {'category': 'strength', 'theme': 'problem solving', 'frequency': 6}
        ]
    )
    
    engine = R2C2Engine(feedback)
    
    # Test 1: Relationship phase prompt
    print("\n1. Testing Relationship phase prompt...")
    prompt = engine.get_phase_prompt(include_emotional_guidance=False)
    
    assert 'RELATIONSHIP BUILDING' in prompt
    assert 'rapport' in prompt.lower() or 'trust' in prompt.lower()
    assert 'psychological safety' in prompt.lower() or 'safe space' in prompt.lower()
    print("   ✓ Relationship prompt contains rapport-building guidance")
    print(f"   ✓ Prompt length: {len(prompt)} characters")
    
    # Test 2: Reaction phase prompt
    print("\n2. Testing Reaction phase prompt...")
    engine.transition_to_next_phase()
    prompt = engine.get_phase_prompt(include_emotional_guidance=False)
    
    assert 'REACTION EXPLORATION' in prompt
    assert 'defensive' in prompt.lower()
    assert 'emotion' in prompt.lower()
    assert 'feedback' in prompt.lower()
    print("   ✓ Reaction prompt contains emotion exploration guidance")
    print(f"   ✓ Prompt length: {len(prompt)} characters")
    
    # Test 3: Content phase prompt
    print("\n3. Testing Content phase prompt...")
    engine.transition_to_next_phase()
    prompt = engine.get_phase_prompt(include_emotional_guidance=False)
    
    assert 'CONTENT DISCUSSION' in prompt
    assert 'pattern' in prompt.lower() or 'theme' in prompt.lower()
    assert 'behavior' in prompt.lower()
    # Check if feedback themes are included
    assert 'time management' in prompt.lower() or 'problem solving' in prompt.lower()
    print("   ✓ Content prompt contains feedback analysis guidance")
    print("   ✓ Feedback themes are included in prompt")
    print(f"   ✓ Prompt length: {len(prompt)} characters")
    
    # Test 4: Coaching phase prompt
    print("\n4. Testing Coaching phase prompt...")
    engine.transition_to_next_phase()
    prompt = engine.get_phase_prompt(include_emotional_guidance=False)
    
    assert 'COACHING FOR CHANGE' in prompt
    assert 'SMART' in prompt or 'goal' in prompt.lower()
    assert 'action' in prompt.lower() or 'development' in prompt.lower()
    print("   ✓ Coaching prompt contains goal-setting guidance")
    print(f"   ✓ Prompt length: {len(prompt)} characters")
    
    # Test 5: Emotional adaptation guidance
    print("\n5. Testing emotional adaptation guidance...")
    
    # Add defensive emotion
    engine.state.emotional_states.append(EmotionState(
        emotion='defensive',
        confidence=0.8,
        timestamp=datetime.now()
    ))
    
    prompt_with_emotion = engine.get_phase_prompt(include_emotional_guidance=True)
    assert 'EMOTIONAL ADAPTATION' in prompt_with_emotion
    assert 'DEFENSIVE' in prompt_with_emotion
    assert 'SLOW DOWN' in prompt_with_emotion or 'slow down' in prompt_with_emotion.lower()
    print("   ✓ Emotional guidance included when requested")
    print("   ✓ Defensive emotion guidance present")
    
    # Test 6: Phase guidance structure
    print("\n6. Testing phase guidance structure...")
    guidance = engine.get_phase_guidance()
    
    assert 'phase' in guidance
    assert 'goals' in guidance
    assert 'key_questions' in guidance
    assert 'tips' in guidance
    assert guidance['phase'] == 'coaching'
    assert len(guidance['goals']) > 0
    assert len(guidance['key_questions']) > 0
    print(f"   ✓ Guidance structure complete")
    print(f"   ✓ Goals: {len(guidance['goals'])}")
    print(f"   ✓ Key questions: {len(guidance['key_questions'])}")
    print(f"   ✓ Tips: {len(guidance['tips'])}")
    
    print("\n" + "="*70)
    print("✓ All phase prompt correctness tests passed!")
    print("="*70)


def run_all_tests():
    """Run all phase transition tests."""
    print("\n" + "="*70)
    print("R2C2 PHASE TRANSITION TEST SUITE")
    print("="*70)
    print("\nTesting Requirements:")
    print("- 14.2: R2C2 conversation engine phase transitions")
    print("- 14.3: Emotion-based transition logic")
    print("="*70)
    
    try:
        test_automatic_time_based_transitions()
        test_emotion_based_transitions()
        test_manual_phase_progression()
        test_phase_prompts_correctness()
        
        print("\n" + "="*70)
        print("✓✓✓ ALL PHASE TRANSITION TESTS PASSED ✓✓✓")
        print("="*70)
        print("\nSummary:")
        print("✓ Automatic time-based transitions work correctly")
        print("✓ Emotion-based transitions function as expected")
        print("✓ Manual phase progression operates properly")
        print("✓ Phase prompts contain correct guidance")
        print("\nThe R2C2 phase transition system is working correctly!")
        
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
