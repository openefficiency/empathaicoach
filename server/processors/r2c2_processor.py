"""R2C2 Processor for Pipecat Pipeline.

This processor integrates the R2C2 conversation engine into the Pipecat pipeline.
It handles:
- Injecting phase-specific context into LLM prompts
- Managing phase transitions based on R2C2Engine state
- Recording user responses and emotional states
- Emitting phase transition events to the frontend
"""

from datetime import datetime
from loguru import logger
from pipecat.frames.frames import (
    Frame,
    LLMMessagesFrame,
    SystemFrame,
    TextFrame,
    TranscriptionFrame,
)
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.processors.frameworks.rtvi import RTVIProcessor

from r2c2.engine import R2C2Engine, EmotionState
from r2c2.emotion_detector import EmotionType


class R2C2Processor(FrameProcessor):
    """Processor that integrates R2C2 framework logic into the pipeline.
    
    This processor:
    1. Monitors user transcriptions and records them in the R2C2 engine
    2. Checks for phase transitions based on time and emotional state
    3. Injects phase-specific prompts into LLM messages
    4. Emits phase transition events via RTVI for frontend updates
    """
    
    def __init__(
        self,
        r2c2_engine: R2C2Engine,
        rtvi_processor: RTVIProcessor = None,
        **kwargs
    ):
        """Initialize the R2C2 processor.
        
        Args:
            r2c2_engine: The R2C2 conversation engine instance
            rtvi_processor: Optional RTVI processor for emitting events
            **kwargs: Additional arguments for FrameProcessor
        """
        super().__init__(**kwargs)
        self.r2c2_engine = r2c2_engine
        self.rtvi_processor = rtvi_processor
        self._last_phase = r2c2_engine.get_current_phase()
        self._phase_prompt_injected = False
        
        logger.info(f"R2C2Processor initialized in {self._last_phase.value} phase")
    
    async def process_frame(self, frame: Frame, direction: str):
        """Process frames through the R2C2 logic.
        
        Args:
            frame: The frame to process
            direction: Frame direction ('upstream' or 'downstream')
        """
        # Call parent to handle StartFrame and other system frames properly
        await super().process_frame(frame, direction)
        
        try:
            # Handle user transcriptions
            if isinstance(frame, TranscriptionFrame):
                await self._handle_user_transcription(frame)
            
            # Handle LLM message frames to inject phase context
            elif isinstance(frame, LLMMessagesFrame):
                await self._inject_phase_context(frame)
        
        except Exception as e:
            logger.error(f"R2C2Processor: Error processing frame: {e}")
            # Continue processing despite errors to maintain conversation flow
    
    async def _handle_user_transcription(self, frame: TranscriptionFrame):
        """Handle user transcription and update R2C2 state.
        
        Args:
            frame: User transcription frame
        """
        try:
            user_text = frame.text
            
            if not user_text or len(user_text.strip()) == 0:
                return
            
            logger.debug(f"R2C2: Recording user response: {user_text[:50]}...")
            
            # Record the user response in the R2C2 engine
            # Note: Emotion state will be added by EmotionProcessor
            self.r2c2_engine.record_user_response(user_text)
            
            # Check if we should transition to the next phase
            current_phase = self.r2c2_engine.get_current_phase()
            should_transition = self.r2c2_engine.should_transition()
            
            if should_transition:
                new_phase = self.r2c2_engine.transition_to_next_phase()
                
                if new_phase != current_phase:
                    logger.info(f"R2C2: Phase transition: {current_phase.value} -> {new_phase.value}")
                    self._last_phase = new_phase
                    self._phase_prompt_injected = False
                    
                    # Emit phase transition event to frontend
                    await self._emit_phase_transition_event(current_phase, new_phase)
        
        except Exception as e:
            logger.error(f"R2C2Processor: Error handling user transcription: {e}")
            # Continue despite error to maintain conversation flow
    
    async def _inject_phase_context(self, frame: LLMMessagesFrame):
        """Inject R2C2 phase-specific context into LLM messages.
        
        Args:
            frame: LLM messages frame to modify
        """
        try:
            current_phase = self.r2c2_engine.get_current_phase()
            
            # Check if phase changed or if we haven't injected yet
            # Also check if emotional state has changed significantly
            should_update_prompt = (
                current_phase != self._last_phase or 
                not self._phase_prompt_injected or
                self._should_update_for_emotion()
            )
            
            if should_update_prompt:
                # Get phase-specific prompt with emotional adaptation
                phase_prompt = self.r2c2_engine.get_phase_prompt(include_emotional_guidance=True)
                
                # Inject as system message at the beginning
                # This ensures the LLM has the current phase context
                if frame.messages and len(frame.messages) > 0:
                    # Check if first message is a system message
                    if frame.messages[0].get("role") == "system":
                        # Update existing system message
                        existing_content = frame.messages[0].get("content", "")
                        frame.messages[0]["content"] = f"{existing_content}\n\n{phase_prompt}"
                    else:
                        # Insert new system message at the beginning
                        frame.messages.insert(0, {
                            "role": "system",
                            "content": phase_prompt
                        })
                else:
                    # No messages yet, add system message
                    frame.messages = [{
                        "role": "system",
                        "content": phase_prompt
                    }]
                
                self._phase_prompt_injected = True
                self._last_phase = current_phase
                
                logger.debug(f"R2C2: Injected {current_phase.value} phase prompt with emotional adaptation into LLM context")
        
        except Exception as e:
            logger.error(f"R2C2Processor: Error injecting phase context: {e}")
            # Continue despite error - LLM will use base instruction
    
    def _should_update_for_emotion(self) -> bool:
        """Check if prompt should be updated due to emotional state change.
        
        Returns:
            True if emotional state has changed significantly
        """
        try:
            # Get recent emotions
            recent_emotions = self.r2c2_engine.get_recent_emotions(window_seconds=30)
            
            if len(recent_emotions) < 2:
                return False
            
            # Check if there's been a significant emotional shift
            # Compare the most recent emotion to emotions from 20-30 seconds ago
            current_emotion = recent_emotions[-1].emotion
            
            # Get emotions from 20-30 seconds ago
            older_emotions = [e for e in recent_emotions if 
                            (recent_emotions[-1].timestamp - e.timestamp).total_seconds() >= 20]
            
            if not older_emotions:
                return False
            
            older_emotion = older_emotions[0].emotion
            
            # Significant shift if emotion changed from/to defensive, frustrated, sad, or anxious
            significant_emotions = {'defensive', 'frustrated', 'sad', 'anxious'}
            
            # If we moved into or out of a significant emotion state, update
            if (current_emotion in significant_emotions) != (older_emotion in significant_emotions):
                logger.debug(f"R2C2: Significant emotional shift detected: {older_emotion} -> {current_emotion}")
                return True
            
            # If we changed between different significant emotions, update
            if (current_emotion in significant_emotions and 
                older_emotion in significant_emotions and 
                current_emotion != older_emotion):
                logger.debug(f"R2C2: Emotional state changed: {older_emotion} -> {current_emotion}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"R2C2Processor: Error checking emotional state: {e}")
            return False
    
    async def _emit_phase_transition_event(self, from_phase, to_phase):
        """Emit phase transition event to frontend via RTVI.
        
        Args:
            from_phase: Previous R2C2 phase
            to_phase: New R2C2 phase
        """
        if not self.rtvi_processor:
            logger.warning("R2C2: No RTVI processor available for phase transition event")
            return
        
        try:
            # Emit custom RTVI event
            event_data = {
                "type": "r2c2-phase-transition",
                "data": {
                    "from_phase": from_phase.value,
                    "to_phase": to_phase.value,
                    "timestamp": datetime.now().isoformat(),
                    "time_in_previous_phase": self.r2c2_engine.get_time_in_phase()
                }
            }
            
            # Use RTVI to send custom server message
            await self.rtvi_processor.send_server_message(event_data)
            
            logger.info(f"R2C2: Emitted phase transition event: {from_phase.value} -> {to_phase.value}")
        
        except Exception as e:
            logger.error(f"R2C2: Failed to emit phase transition event: {e}")
    
    def get_current_phase(self):
        """Get the current R2C2 phase.
        
        Returns:
            Current R2C2Phase enum value
        """
        return self.r2c2_engine.get_current_phase()
    
    def get_phase_guidance(self):
        """Get guidance for the current phase.
        
        Returns:
            Dictionary with phase guidance
        """
        return self.r2c2_engine.get_phase_guidance()
    
    def get_session_summary(self):
        """Get the session summary from the R2C2 engine.
        
        Returns:
            Dictionary with session summary data
        """
        return self.r2c2_engine.get_session_summary()
