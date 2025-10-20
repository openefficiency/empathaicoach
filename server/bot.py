#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""R2C2 Voice Coach Bot Implementation.

This module implements an emotionally intelligent AI coach using the R2C2 framework
for processing 360° feedback. It includes:

- Real-time voice interaction with emotion detection
- R2C2 framework phase management (Relationship, Reaction, Content, Coaching)
- Session persistence and development plan tracking
- Adaptive coaching based on emotional state

The bot runs as part of a Pipecat pipeline that processes audio frames and manages
the conversation flow using Gemini's multimodal capabilities.
"""

import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from google.genai.types import ThinkingConfig
from loguru import logger
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (
    LLMRunFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.google.gemini_live.llm import GeminiLiveLLMService, InputParams
from pipecat.transports.base_transport import BaseTransport
from pipecat.transports.daily.transport import DailyParams

# Import R2C2 components
from r2c2.engine import R2C2Engine, FeedbackData
from r2c2.emotion_detector import EmotionDetector
from processors.r2c2_processor import R2C2Processor
from processors.emotion_processor import EmotionProcessor
from database.session_db import SessionDatabase

load_dotenv(override=True)

# Base system instruction for the R2C2 Voice Coach
BASE_SYSTEM_INSTRUCTION = """You are an emotionally intelligent AI coach trained in the R2C2 framework for processing 360° feedback. Your role is to guide employees through a structured conversation that reduces defensiveness and helps them create actionable development plans.

## Your Core Identity

You are a supportive, empathetic coach who creates a safe space for difficult conversations. You understand that receiving feedback—especially critical feedback—can trigger defensiveness, anxiety, and self-doubt. Your presence is warm, non-judgmental, and genuinely curious about the person's experience.

## Core Principles

**Emotional Intelligence:**
- Recognize and validate emotional cues in the user's speech (frustration, sadness, defensiveness, anxiety)
- When you sense strong emotions, slow down and provide space for processing
- Validate feelings without reinforcing defensiveness ("It makes sense you'd feel that way" vs. "You're right to be upset")
- Adapt your pacing based on emotional state—don't rush someone who's processing difficult feelings

**Communication Style:**
- Speak naturally and conversationally, like a trusted colleague, not a therapist or corporate trainer
- Use open-ended questions to promote self-reflection ("What comes up for you when you hear that?" vs. "Do you agree?")
- Avoid corporate jargon and buzzwords—be authentic and human
- Keep responses concise and focused—this is a conversation, not a lecture
- Use "I" statements to share observations ("I'm noticing..." "I'm hearing...")

**Coaching Approach:**
- Be genuinely curious about their perspective and experience
- Celebrate progress and insights specifically ("I appreciate how you're connecting those dots")
- Maintain appropriate boundaries—you're a professional coach, not a therapist
- Focus on behaviors and impact, not character or identity
- Help them discover insights rather than telling them what to think

**R2C2 Framework Fidelity:**
The R2C2 framework has four sequential phases. Each phase has a specific purpose:

1. **RELATIONSHIP**: Build rapport and create psychological safety (2-3 minutes)
   - Establish trust before diving into difficult topics
   - Acknowledge the challenge of receiving feedback
   
2. **REACTION**: Explore emotional reactions to feedback (3-5 minutes)
   - Process defensiveness and strong emotions
   - Normalize reactions without reinforcing them
   - Wait for emotional readiness before moving forward
   
3. **CONTENT**: Discuss and understand the feedback objectively (4-6 minutes)
   - Help them see patterns and themes
   - Distinguish behavior from identity
   - Explore different perspectives
   
4. **COACHING**: Create actionable development plans (5-8 minutes)
   - Focus on 1-3 priority areas
   - Create SMART goals with specific behaviors
   - Identify obstacles and support systems

You will receive phase-specific guidance as the conversation progresses. Follow that guidance while maintaining your warm, supportive coaching style. Trust the process—each phase builds on the previous one.

## Key Reminders

- This is about growth, not judgment
- Defensiveness is normal and expected—it's part of the process
- Small insights and commitments are more valuable than grand plans
- Your role is to guide, not to fix or solve
- The employee is the expert on their own experience
"""


# Global session state (will be set during bot initialization)
current_session_id: Optional[int] = None
session_db: Optional[SessionDatabase] = None
r2c2_engine: Optional[R2C2Engine] = None


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    """Main bot execution function.

    Sets up and runs the bot pipeline including:
    - R2C2 conversation engine
    - Emotion detection
    - Gemini Live multimodal model integration
    - Session persistence
    - Voice activity detection
    - RTVI event handling
    """
    global current_session_id, session_db, r2c2_engine

    # Initialize database
    session_db = SessionDatabase()
    logger.info("Session database initialized")

    # Get feedback data from runner args or use sample data
    # In production, this would come from the API endpoint
    feedback_data = _get_feedback_data(runner_args)
    user_id = getattr(runner_args, 'user_id', 'default_user')

    # Create session in database
    try:
        current_session_id = session_db.create_session(
            user_id=user_id,
            feedback_data=feedback_data
        )
        logger.info(f"Created session {current_session_id} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        current_session_id = None

    # Initialize R2C2 Engine with feedback data
    feedback_obj = FeedbackData(
        feedback_id=feedback_data.get('feedback_id', 'sample_feedback'),
        user_id=user_id,
        collection_date=datetime.now(),
        themes=feedback_data.get('themes', []),
        raw_comments=feedback_data.get('raw_comments', [])
    )
    r2c2_engine = R2C2Engine(feedback_data=feedback_obj)
    logger.info(f"R2C2 Engine initialized in {r2c2_engine.get_current_phase().value} phase")

    # Initialize Emotion Detector
    # Note: Emotion detection failures are handled gracefully in EmotionProcessor
    # If emotion detection fails, the system continues with neutral emotion state
    emotion_detector = EmotionDetector()
    logger.info("Emotion Detector initialized")

    # Initialize the Gemini Multimodal Live model
    try:
        llm = GeminiLiveLLMService(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini-2.5-flash-native-audio-preview-09-2025",
            voice_id="Kore",  # Warm, empathetic voice for coaching
            system_instruction=BASE_SYSTEM_INSTRUCTION,
            params=InputParams(thinking=ThinkingConfig(thinking_budget=0)),
        )
        logger.info("Gemini LLM service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini LLM service: {e}")
        raise RuntimeError(f"Cannot start bot without LLM service: {e}")

    # Initial message to start the conversation with R2C2 phase context
    initial_phase_prompt = r2c2_engine.get_phase_prompt(include_emotional_guidance=False)
    messages = [
        {
            "role": "system",
            "content": initial_phase_prompt,
        },
        {
            "role": "user",
            "content": "Please introduce yourself and begin the coaching session.",
        },
    ]

    # Set up conversation context and management
    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    # RTVI events for Pipecat client UI
    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    # Create custom processors
    r2c2_processor = R2C2Processor(
        r2c2_engine=r2c2_engine,
        rtvi_processor=rtvi
    )
    logger.info("R2C2 Processor created")

    emotion_processor = EmotionProcessor(
        emotion_detector=emotion_detector,
        r2c2_engine=r2c2_engine,
        rtvi_processor=rtvi
    )
    logger.info("Emotion Processor created")

    # Build pipeline with R2C2 components
    # NOTE: Temporarily simplified pipeline for debugging
    pipeline = Pipeline(
        [
            transport.input(),
            rtvi,
            context_aggregator.user(),
            # r2c2_processor,      # Process R2C2 logic and phase transitions
            # emotion_processor,   # Detect emotions from audio
            llm,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        """Handle client ready event."""
        await rtvi.set_bot_ready()
        logger.info("Client ready, starting conversation")
        
        # Start the conversation - the initial message is already in the context
        await task.queue_frames([LLMRunFrame()])
        logger.info("Queued LLMRunFrame to start conversation")

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, participant):
        """Handle client connection."""
        logger.info(f"Client connected: {participant.get('id', 'unknown')}")
        
        # Check if this is a reconnection (session already exists)
        # In production, this would check for an existing session ID from the client
        # For now, we always create a new session, but the infrastructure is here
        
        # Emit initial phase event to frontend via RTVI processor
        try:
            current_phase = r2c2_engine.get_current_phase()
            # Queue a message frame to send phase update
            from pipecat.frames.frames import OutputTransportMessageFrame
            await task.queue_frames([
                OutputTransportMessageFrame(
                    message={
                        "type": "r2c2-phase-update",
                        "data": {
                            "phase": current_phase.value,
                            "session_id": current_session_id,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                )
            ])
        except Exception as e:
            logger.error(f"Failed to emit initial phase event: {e}")

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        """Handle client disconnection and save session state."""
        logger.info("Client disconnected, saving session state")
        
        try:
            # Save session state to database
            if current_session_id and session_db and r2c2_engine:
                await _save_session_state()
                logger.info(f"Session {current_session_id} state saved")
        except Exception as e:
            logger.error(f"Failed to save session state on disconnect: {e}")
        
        # Cancel the task
        await task.cancel()

    # Auto-save session state periodically
    async def auto_save_session():
        """Periodically save session state."""
        import asyncio
        while True:
            try:
                await asyncio.sleep(120)  # Save every 2 minutes
                if current_session_id and session_db and r2c2_engine:
                    await _save_session_state()
                    logger.debug(f"Auto-saved session {current_session_id}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")

    # Start auto-save task
    import asyncio
    auto_save_task = asyncio.create_task(auto_save_session())

    try:
        runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
        await runner.run(task)
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        # Try to save state even on error
        if current_session_id and session_db and r2c2_engine:
            try:
                await _save_session_state()
                logger.info("Session state saved after error")
            except Exception as save_error:
                logger.error(f"Failed to save state after error: {save_error}")
        raise
    finally:
        # Cancel auto-save and save final state
        auto_save_task.cancel()
        try:
            await auto_save_task
        except asyncio.CancelledError:
            pass
        
        # Final save and session end
        if current_session_id and session_db and r2c2_engine:
            try:
                await _save_session_state()
                await _end_session()
                logger.info(f"Session {current_session_id} ended successfully")
            except Exception as e:
                logger.error(f"Failed to end session: {e}")


async def _save_session_state():
    """Save current session state to database."""
    global current_session_id, session_db, r2c2_engine
    
    if not all([current_session_id, session_db, r2c2_engine]):
        return
    
    try:
        # Get current state from R2C2 engine
        state = r2c2_engine.get_state()
        
        # Prepare state data for storage
        state_data = {
            'current_phase': state.current_phase.value,
            'phase_start_time': state.phase_start_time.isoformat(),
            'user_reactions': state.user_reactions,
            'content_themes': state.content_themes,
            'phase_history': state.phase_history,
            'last_saved': datetime.now().isoformat()
        }
        
        # Update session with current state
        session_db.update_session_state(current_session_id, state_data)
        
    except Exception as e:
        logger.error(f"Error saving session state: {e}")
        raise


async def _restore_session_state(session_id: int) -> bool:
    """Restore session state from database.
    
    Args:
        session_id: The session ID to restore
        
    Returns:
        True if restoration was successful, False otherwise
    """
    global session_db, r2c2_engine
    
    if not all([session_db, r2c2_engine]):
        return False
    
    try:
        # Get session data from database
        session_data = session_db.get_session_by_id(session_id)
        
        if not session_data or not session_data.get('session_summary'):
            logger.warning(f"No saved state found for session {session_id}")
            return False
        
        # Parse saved state
        saved_state = session_data['session_summary']
        
        # Restore R2C2 engine state
        from r2c2.engine import R2C2Phase, R2C2State
        
        # Reconstruct the state
        restored_state = r2c2_engine.get_state()
        
        # Restore phase information
        if 'current_phase' in saved_state:
            restored_state.current_phase = R2C2Phase(saved_state['current_phase'])
        
        if 'phase_start_time' in saved_state:
            restored_state.phase_start_time = datetime.fromisoformat(saved_state['phase_start_time'])
        
        if 'user_reactions' in saved_state:
            restored_state.user_reactions = saved_state['user_reactions']
        
        if 'content_themes' in saved_state:
            restored_state.content_themes = saved_state['content_themes']
        
        if 'phase_history' in saved_state:
            restored_state.phase_history = saved_state['phase_history']
        
        # Apply restored state
        r2c2_engine.restore_state(restored_state)
        
        logger.info(f"Successfully restored session {session_id} state")
        logger.info(f"Restored to phase: {restored_state.current_phase.value}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error restoring session state: {e}")
        return False


async def _end_session():
    """End the session and generate summary."""
    global current_session_id, session_db, r2c2_engine
    
    if not all([current_session_id, session_db, r2c2_engine]):
        return
    
    try:
        # Generate session summary
        summary = r2c2_engine.get_session_summary()
        summary['session_id'] = current_session_id
        
        # Save summary to database
        session_db.end_session(current_session_id, summary)
        
        # Save development plan if it exists
        if r2c2_engine.state.development_plan and r2c2_engine.state.development_plan.goals:
            goals = []
            for goal in r2c2_engine.state.development_plan.goals:
                goals.append({
                    'goal_text': goal.get('description', ''),
                    'goal_type': goal.get('type', 'start'),
                    'specific_behavior': goal.get('description', ''),
                    'measurable_criteria': '',
                    'target_date': None,
                    'action_steps': []
                })
            
            if goals:
                session_db.save_development_plan(current_session_id, goals)
                logger.info(f"Saved {len(goals)} development plan goals")
        
        logger.info(f"Session {current_session_id} summary saved")
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise


def _get_feedback_data(runner_args: RunnerArguments) -> dict:
    """Get feedback data from runner args or return sample data.
    
    Args:
        runner_args: Runner arguments that may contain feedback data
        
    Returns:
        Dictionary containing feedback data
    """
    # Check if feedback data was provided in runner args
    if hasattr(runner_args, 'feedback_data'):
        return runner_args.feedback_data
    
    # Return sample feedback data for testing
    return {
        'feedback_id': 'sample_360_feedback',
        'themes': [
            {
                'category': 'improvement',
                'theme': 'Communication clarity',
                'frequency': 5,
                'examples': [
                    'Could be more clear in written communications',
                    'Sometimes assumptions are made without clarifying'
                ]
            },
            {
                'category': 'strength',
                'theme': 'Technical expertise',
                'frequency': 8,
                'examples': [
                    'Deep knowledge of the technology stack',
                    'Go-to person for technical questions'
                ]
            },
            {
                'category': 'improvement',
                'theme': 'Delegation and empowerment',
                'frequency': 4,
                'examples': [
                    'Could delegate more to team members',
                    'Sometimes takes on too much individually'
                ]
            }
        ],
        'raw_comments': [
            {
                'source': 'manager',
                'category': 'communication',
                'comment': 'Great technical skills, but could improve on communicating complex ideas to non-technical stakeholders',
                'sentiment': 'neutral'
            },
            {
                'source': 'peer',
                'category': 'collaboration',
                'comment': 'Always willing to help and share knowledge',
                'sentiment': 'positive'
            }
        ]
    }


async def bot(runner_args: RunnerArguments):
    """Main bot entry point for the bot starter."""

    try:
        # Krisp is available when deployed to Pipecat Cloud
        if os.environ.get("ENV") != "local":
            try:
                from pipecat.audio.filters.krisp_filter import KrispFilter
                krisp_filter = KrispFilter()
                logger.info("Krisp audio filter enabled")
            except ImportError:
                logger.warning("Krisp filter not available, proceeding without it")
                krisp_filter = None
        else:
            krisp_filter = None

        transport_params = {
            "daily": lambda: DailyParams(
                audio_in_enabled=True,
                audio_in_filter=krisp_filter,
                audio_out_enabled=True,
                video_in_enabled=False,  # No video needed for voice coaching
                vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
                turn_analyzer=LocalSmartTurnAnalyzerV3(),
            )
        }

        transport = await create_transport(runner_args, transport_params)
        logger.info("Transport created successfully")

        await run_bot(transport, runner_args)
        
    except Exception as e:
        logger.error(f"Fatal error in bot: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Monkey-patch Pipecat's _setup_daily_routes to add our custom routes
    import pipecat.runner.run as runner_module
    from contextlib import asynccontextmanager
    
    original_setup_daily_routes = runner_module._setup_daily_routes
    
    def custom_setup_daily_routes(app):
        """Setup Daily routes plus our custom API routes."""
        # Call original setup
        original_setup_daily_routes(app)
        
        # Add our custom routes
        from api.routes import router
        from database.session_db import SessionDatabase
        from api import server as api_server
        
        # Initialize database
        api_server.db = SessionDatabase()
        logger.info("Database initialized for custom API routes")
        
        # Add our routes
        app.include_router(router, prefix="/api")
        logger.info("Custom API routes added to Pipecat server")
    
    # Replace the function
    runner_module._setup_daily_routes = custom_setup_daily_routes
    
    # Now start the Pipecat runner
    from pipecat.runner.run import main
    main()
