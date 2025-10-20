"""Emotion Processor for Pipecat Pipeline.

This processor integrates emotion detection into the Pipecat pipeline.
It handles:
- Processing audio frames through the EmotionDetector
- Emitting emotion events to the frontend via RTVI
- Storing emotion data in the R2C2Engine for phase transition decisions
"""

import numpy as np
from datetime import datetime
from loguru import logger
from pipecat.frames.frames import (
    Frame,
    InputAudioRawFrame,
)
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.processors.frameworks.rtvi import RTVIProcessor

from r2c2.emotion_detector import EmotionDetector, EmotionState, EmotionType
from r2c2.engine import R2C2Engine


class EmotionProcessor(FrameProcessor):
    """Processor that detects emotions from audio and integrates with R2C2.
    
    This processor:
    1. Analyzes audio frames to detect emotional states
    2. Emits emotion events to the frontend via RTVI
    3. Stores emotion data in the R2C2 engine for phase transitions
    4. Provides real-time emotion feedback to enhance coaching
    """
    
    # Process every Nth audio frame to reduce computational load
    FRAME_SKIP = 10  # Process 1 out of every 10 frames
    
    def __init__(
        self,
        emotion_detector: EmotionDetector,
        r2c2_engine: R2C2Engine = None,
        rtvi_processor: RTVIProcessor = None,
        **kwargs
    ):
        """Initialize the emotion processor.
        
        Args:
            emotion_detector: The EmotionDetector instance
            r2c2_engine: Optional R2C2 engine to store emotion data
            rtvi_processor: Optional RTVI processor for emitting events
            **kwargs: Additional arguments for FrameProcessor
        """
        super().__init__(**kwargs)
        self.emotion_detector = emotion_detector
        self.r2c2_engine = r2c2_engine
        self.rtvi_processor = rtvi_processor
        
        # Frame processing control
        self._frame_count = 0
        self._last_emotion = None
        self._last_emotion_time = None
        
        # Audio buffer for accumulating samples
        self._audio_buffer = []
        self._buffer_size = 16000  # 1 second at 16kHz
        
        logger.info("EmotionProcessor initialized")
    
    async def process_frame(self, frame: Frame, direction: str):
        """Process frames for emotion detection.
        
        Args:
            frame: The frame to process
            direction: Frame direction ('upstream' or 'downstream')
        """
        # Call parent to handle StartFrame and other system frames properly
        await super().process_frame(frame, direction)
        
        # Only process audio frames
        if isinstance(frame, InputAudioRawFrame):
            await self._process_audio_frame(frame)
    
    async def _process_audio_frame(self, frame: InputAudioRawFrame):
        """Process audio frame for emotion detection.
        
        Args:
            frame: Audio frame to analyze
        """
        # Skip frames to reduce processing load
        self._frame_count += 1
        if self._frame_count % self.FRAME_SKIP != 0:
            return
        
        try:
            # Get audio data from frame
            audio_data = frame.audio
            
            # Convert to numpy array if needed
            if not isinstance(audio_data, np.ndarray):
                audio_data = np.frombuffer(audio_data, dtype=np.int16)
            
            # Normalize to float32 in range [-1, 1]
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            
            # Add to buffer
            self._audio_buffer.extend(audio_data)
            
            # Process when buffer is full
            if len(self._audio_buffer) >= self._buffer_size:
                await self._analyze_buffered_audio()
        
        except Exception as e:
            logger.error(f"EmotionProcessor: Error processing audio frame: {e}")
    
    async def _analyze_buffered_audio(self):
        """Analyze accumulated audio buffer for emotion."""
        try:
            # Convert buffer to numpy array
            audio_array = np.array(self._audio_buffer[:self._buffer_size], dtype=np.float32)
            
            # Clear processed samples from buffer
            self._audio_buffer = self._audio_buffer[self._buffer_size:]
            
            # Skip if audio is too quiet (likely silence)
            rms = np.sqrt(np.mean(audio_array ** 2))
            if rms < 0.01:  # Silence threshold
                return
            
            # Analyze emotion
            emotion_state = self.emotion_detector.analyze_audio(
                audio_array,
                sample_rate=16000
            )
            
            # Check if emotion changed significantly
            if self._should_emit_emotion(emotion_state):
                # Store in R2C2 engine if available
                if self.r2c2_engine:
                    self.r2c2_engine.state.emotional_states.append(emotion_state)
                
                # Emit to frontend
                await self._emit_emotion_event(emotion_state)
                
                # Update last emotion
                self._last_emotion = emotion_state.emotion
                self._last_emotion_time = emotion_state.timestamp
                
                logger.debug(
                    f"EmotionProcessor: Detected {emotion_state.emotion.value} "
                    f"(confidence: {emotion_state.confidence:.2f})"
                )
        
        except Exception as e:
            logger.error(f"EmotionProcessor: Error analyzing audio: {e}")
    
    def _should_emit_emotion(self, emotion_state: EmotionState) -> bool:
        """Determine if we should emit this emotion event.
        
        We emit when:
        1. This is the first emotion detected
        2. The emotion changed from the last one
        3. It's been more than 10 seconds since last emission
        4. Confidence is above threshold
        
        Args:
            emotion_state: The detected emotion state
            
        Returns:
            True if should emit the emotion event
        """
        # Check confidence threshold
        if emotion_state.confidence < 0.4:
            return False
        
        # First emotion
        if self._last_emotion is None:
            return True
        
        # Emotion changed
        if emotion_state.emotion != self._last_emotion:
            return True
        
        # Time threshold (emit periodic updates)
        if self._last_emotion_time:
            time_since_last = (emotion_state.timestamp - self._last_emotion_time).total_seconds()
            if time_since_last >= 10:  # 10 seconds
                return True
        
        return False
    
    async def _emit_emotion_event(self, emotion_state: EmotionState):
        """Emit emotion event to frontend via RTVI.
        
        Args:
            emotion_state: The emotion state to emit
        """
        if not self.rtvi_processor:
            logger.debug("EmotionProcessor: No RTVI processor available for emotion event")
            return
        
        try:
            # Get current R2C2 phase if available
            current_phase = None
            if self.r2c2_engine:
                current_phase = self.r2c2_engine.get_current_phase().value
            
            # Prepare event data
            event_data = {
                "type": "emotion-detected",
                "data": {
                    "emotion": emotion_state.emotion.value,
                    "confidence": round(emotion_state.confidence, 2),
                    "timestamp": emotion_state.timestamp.isoformat(),
                    "r2c2_phase": current_phase,
                    "audio_features": {
                        k: round(v, 2) for k, v in emotion_state.audio_features.items()
                    }
                }
            }
            
            # Send via RTVI
            await self.rtvi_processor.send_server_message(event_data)
            
            logger.debug(f"EmotionProcessor: Emitted emotion event: {emotion_state.emotion.value}")
        
        except Exception as e:
            logger.error(f"EmotionProcessor: Failed to emit emotion event: {e}")
    
    def get_current_emotion(self) -> EmotionType:
        """Get the most recently detected emotion.
        
        Returns:
            Current emotion type or NEUTRAL if none detected
        """
        if self._last_emotion:
            return self._last_emotion
        return EmotionType.NEUTRAL
    
    def get_emotion_trend(self, window_seconds: int = 30) -> EmotionType:
        """Get the emotion trend over a time window.
        
        Args:
            window_seconds: Time window to analyze
            
        Returns:
            Predominant emotion in the window
        """
        return self.emotion_detector.get_emotion_trend(window_seconds)
    
    def is_emotionally_ready(self) -> bool:
        """Check if user is emotionally ready for phase transition.
        
        Returns:
            True if emotions indicate readiness
        """
        return self.emotion_detector.is_emotionally_ready_for_transition()
    
    def reset(self):
        """Reset the emotion processor state."""
        self._frame_count = 0
        self._last_emotion = None
        self._last_emotion_time = None
        self._audio_buffer = []
        self.emotion_detector.reset()
        logger.info("EmotionProcessor: State reset")
