"""Emotion Detection Module.

This module implements real-time emotion detection from voice audio using
acoustic features like pitch, energy, and tempo. It provides emotion analysis
to inform R2C2 phase transitions and coaching adaptations.
"""

import numpy as np
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


class EmotionType(Enum):
    """Types of emotions detected from voice."""
    
    NEUTRAL = "neutral"
    DEFENSIVE = "defensive"
    FRUSTRATED = "frustrated"
    SAD = "sad"
    ANXIOUS = "anxious"
    POSITIVE = "positive"


@dataclass
class EmotionState:
    """Emotional state at a point in time."""
    
    emotion: EmotionType
    confidence: float
    timestamp: datetime
    audio_features: Dict[str, float] = field(default_factory=dict)


class EmotionDetector:
    """Detects emotions from voice audio using acoustic features.
    
    This detector uses heuristic-based classification analyzing:
    - Pitch variance (fundamental frequency)
    - Energy levels (volume/intensity)
    - Speaking rate (tempo)
    
    The detector maintains a history of emotion states for trend analysis
    and phase transition decisions.
    """
    
    # Audio feature thresholds for emotion classification
    # These are heuristic values that can be tuned based on testing
    PITCH_VARIANCE_HIGH = 50.0  # Hz variance
    PITCH_VARIANCE_LOW = 15.0
    ENERGY_HIGH = 0.7  # Normalized 0-1
    ENERGY_LOW = 0.3
    TEMPO_FAST = 1.3  # Relative to baseline
    TEMPO_SLOW = 0.7
    
    # Confidence thresholds
    MIN_CONFIDENCE = 0.3
    HIGH_CONFIDENCE = 0.7
    
    def __init__(self, history_window_seconds: int = 300):
        """Initialize the emotion detector.
        
        Args:
            history_window_seconds: How long to keep emotion history (default 5 minutes)
        """
        self.history_window = timedelta(seconds=history_window_seconds)
        self.emotion_history: deque = deque()
        
        # Baseline values for normalization (updated during session)
        self.baseline_pitch = 150.0  # Hz (typical speaking pitch)
        self.baseline_energy = 0.5
        self.baseline_tempo = 1.0
        
        # Feature buffers for smoothing
        self.pitch_buffer: deque = deque(maxlen=10)
        self.energy_buffer: deque = deque(maxlen=10)
        self.tempo_buffer: deque = deque(maxlen=10)
    
    def analyze_audio(self, audio_data: np.ndarray, sample_rate: int = 16000) -> EmotionState:
        """Analyze audio data and detect emotion.
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz (default 16000)
            
        Returns:
            EmotionState with detected emotion and confidence
        """
        # Extract audio features
        features = self._extract_audio_features(audio_data, sample_rate)
        
        # Update buffers for smoothing
        self.pitch_buffer.append(features['pitch'])
        self.energy_buffer.append(features['energy'])
        self.tempo_buffer.append(features['tempo'])
        
        # Get smoothed features
        smoothed_features = {
            'pitch': np.mean(list(self.pitch_buffer)),
            'pitch_variance': np.std(list(self.pitch_buffer)),
            'energy': np.mean(list(self.energy_buffer)),
            'tempo': np.mean(list(self.tempo_buffer))
        }
        
        # Classify emotion based on features
        emotion, confidence = self._classify_emotion(smoothed_features)
        
        # Create emotion state
        emotion_state = EmotionState(
            emotion=emotion,
            confidence=confidence,
            timestamp=datetime.now(),
            audio_features=smoothed_features
        )
        
        # Add to history
        self.emotion_history.append(emotion_state)
        self._cleanup_old_history()
        
        return emotion_state
    
    def _extract_audio_features(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int
    ) -> Dict[str, float]:
        """Extract acoustic features from audio data.
        
        Args:
            audio_data: Audio samples
            sample_rate: Sample rate in Hz
            
        Returns:
            Dictionary of extracted features
        """
        # Ensure audio data is not empty
        if len(audio_data) == 0:
            return {
                'pitch': self.baseline_pitch,
                'energy': 0.0,
                'tempo': self.baseline_tempo
            }
        
        # Extract pitch (fundamental frequency) using autocorrelation
        pitch = self._estimate_pitch(audio_data, sample_rate)
        
        # Extract energy (RMS amplitude)
        energy = self._calculate_energy(audio_data)
        
        # Extract tempo (speaking rate) - simplified as zero-crossing rate
        tempo = self._estimate_tempo(audio_data, sample_rate)
        
        return {
            'pitch': pitch,
            'energy': energy,
            'tempo': tempo
        }
    
    def _estimate_pitch(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Estimate pitch using autocorrelation method.
        
        Args:
            audio_data: Audio samples
            sample_rate: Sample rate in Hz
            
        Returns:
            Estimated pitch in Hz
        """
        # Normalize audio
        audio_normalized = audio_data / (np.max(np.abs(audio_data)) + 1e-8)
        
        # Autocorrelation
        correlation = np.correlate(audio_normalized, audio_normalized, mode='full')
        correlation = correlation[len(correlation)//2:]
        
        # Find first peak after initial peak (fundamental frequency)
        # Search in typical human voice range: 80-400 Hz
        min_period = int(sample_rate / 400)  # Max 400 Hz
        max_period = int(sample_rate / 80)   # Min 80 Hz
        
        if max_period >= len(correlation):
            return self.baseline_pitch
        
        # Find peak in valid range
        search_range = correlation[min_period:max_period]
        if len(search_range) == 0:
            return self.baseline_pitch
        
        peak_index = np.argmax(search_range) + min_period
        
        # Convert period to frequency
        if peak_index > 0:
            pitch = sample_rate / peak_index
        else:
            pitch = self.baseline_pitch
        
        # Sanity check
        if pitch < 80 or pitch > 400:
            pitch = self.baseline_pitch
        
        return float(pitch)
    
    def _calculate_energy(self, audio_data: np.ndarray) -> float:
        """Calculate energy (RMS amplitude) of audio.
        
        Args:
            audio_data: Audio samples
            
        Returns:
            Normalized energy value (0-1)
        """
        # Calculate RMS
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Normalize to 0-1 range (assuming 16-bit audio)
        energy = min(rms / 0.1, 1.0)  # 0.1 is a typical speech level
        
        return float(energy)
    
    def _estimate_tempo(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Estimate speaking tempo using zero-crossing rate.
        
        Args:
            audio_data: Audio samples
            sample_rate: Sample rate in Hz
            
        Returns:
            Relative tempo (1.0 = baseline)
        """
        # Calculate zero-crossing rate
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_data)))) / 2
        
        # Normalize by duration
        duration = len(audio_data) / sample_rate
        if duration == 0:
            return self.baseline_tempo
        
        zcr = zero_crossings / duration
        
        # Normalize relative to baseline (typical ZCR ~3000 for speech)
        baseline_zcr = 3000
        tempo = zcr / baseline_zcr
        
        # Clamp to reasonable range
        tempo = max(0.5, min(tempo, 2.0))
        
        return float(tempo)
    
    def _classify_emotion(
        self, 
        features: Dict[str, float]
    ) -> tuple[EmotionType, float]:
        """Classify emotion based on audio features.
        
        Args:
            features: Dictionary of audio features
            
        Returns:
            Tuple of (emotion_type, confidence)
        """
        pitch_variance = features['pitch_variance']
        energy = features['energy']
        tempo = features['tempo']
        
        # Score each emotion based on feature patterns
        emotion_scores = {
            EmotionType.NEUTRAL: 0.0,
            EmotionType.DEFENSIVE: 0.0,
            EmotionType.FRUSTRATED: 0.0,
            EmotionType.SAD: 0.0,
            EmotionType.ANXIOUS: 0.0,
            EmotionType.POSITIVE: 0.0
        }
        
        # Defensive: Higher pitch variance, faster speech, increased energy
        if pitch_variance > self.PITCH_VARIANCE_HIGH:
            emotion_scores[EmotionType.DEFENSIVE] += 0.4
        if tempo > self.TEMPO_FAST:
            emotion_scores[EmotionType.DEFENSIVE] += 0.3
        if energy > self.ENERGY_HIGH:
            emotion_scores[EmotionType.DEFENSIVE] += 0.3
        
        # Frustrated: Elevated energy, irregular tempo, moderate-high pitch variance
        if energy > self.ENERGY_HIGH:
            emotion_scores[EmotionType.FRUSTRATED] += 0.4
        if pitch_variance > self.PITCH_VARIANCE_HIGH * 0.7:
            emotion_scores[EmotionType.FRUSTRATED] += 0.3
        if tempo > self.TEMPO_FAST * 0.9 or tempo < self.TEMPO_SLOW * 1.1:
            emotion_scores[EmotionType.FRUSTRATED] += 0.3
        
        # Sad: Lower energy, slower speech, low pitch variance
        if energy < self.ENERGY_LOW:
            emotion_scores[EmotionType.SAD] += 0.4
        if tempo < self.TEMPO_SLOW:
            emotion_scores[EmotionType.SAD] += 0.3
        if pitch_variance < self.PITCH_VARIANCE_LOW:
            emotion_scores[EmotionType.SAD] += 0.3
        
        # Anxious: High pitch variance, faster tempo, moderate-high energy
        if pitch_variance > self.PITCH_VARIANCE_HIGH:
            emotion_scores[EmotionType.ANXIOUS] += 0.4
        if tempo > self.TEMPO_FAST:
            emotion_scores[EmotionType.ANXIOUS] += 0.3
        if energy > self.ENERGY_HIGH * 0.8:
            emotion_scores[EmotionType.ANXIOUS] += 0.3
        
        # Positive: Moderate energy, steady tempo, moderate pitch variety
        if self.ENERGY_LOW < energy < self.ENERGY_HIGH:
            emotion_scores[EmotionType.POSITIVE] += 0.3
        if self.TEMPO_SLOW * 1.2 < tempo < self.TEMPO_FAST * 0.9:
            emotion_scores[EmotionType.POSITIVE] += 0.4
        if self.PITCH_VARIANCE_LOW < pitch_variance < self.PITCH_VARIANCE_HIGH * 0.8:
            emotion_scores[EmotionType.POSITIVE] += 0.3
        
        # Neutral: Baseline values
        if (self.ENERGY_LOW * 1.2 < energy < self.ENERGY_HIGH * 0.8 and
            self.TEMPO_SLOW * 1.1 < tempo < self.TEMPO_FAST * 0.9 and
            pitch_variance < self.PITCH_VARIANCE_HIGH * 0.6):
            emotion_scores[EmotionType.NEUTRAL] += 0.5
        
        # Find emotion with highest score
        max_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[max_emotion]
        
        # If no strong signal, default to neutral
        if max_score < self.MIN_CONFIDENCE:
            return EmotionType.NEUTRAL, self.MIN_CONFIDENCE
        
        # Normalize confidence to 0-1 range
        confidence = min(max_score, 1.0)
        
        return max_emotion, confidence
    
    def get_emotion_trend(self, window_seconds: int = 30) -> EmotionType:
        """Get the predominant emotion over a time window.
        
        Args:
            window_seconds: Time window to analyze (default 30 seconds)
            
        Returns:
            Most common emotion in the window
        """
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
        
        # Get emotions in window
        recent_emotions = [
            state for state in self.emotion_history
            if state.timestamp >= cutoff_time
        ]
        
        if not recent_emotions:
            return EmotionType.NEUTRAL
        
        # Count emotion frequencies
        emotion_counts = {}
        for state in recent_emotions:
            emotion = state.emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Return most common
        return max(emotion_counts, key=emotion_counts.get)
    
    def is_emotionally_ready_for_transition(self, window_seconds: int = 60) -> bool:
        """Check if emotional state indicates readiness for phase transition.
        
        This method checks if the user has moved from defensive/negative emotions
        to more neutral or positive emotions, indicating readiness to progress.
        
        Args:
            window_seconds: Time window to analyze (default 60 seconds)
            
        Returns:
            True if emotions indicate readiness for transition
        """
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
        
        # Get recent emotions
        recent_emotions = [
            state for state in self.emotion_history
            if state.timestamp >= cutoff_time
        ]
        
        if len(recent_emotions) < 3:
            return False
        
        # Define ready vs. not-ready emotions
        ready_emotions = {EmotionType.NEUTRAL, EmotionType.POSITIVE}
        defensive_emotions = {
            EmotionType.DEFENSIVE, 
            EmotionType.FRUSTRATED, 
            EmotionType.ANXIOUS
        }
        
        # Get most recent sample (last 3 emotions)
        recent_sample = recent_emotions[-3:]
        
        # Count ready emotions in recent sample
        ready_count = sum(
            1 for state in recent_sample
            if state.emotion in ready_emotions
        )
        
        # Check if majority are ready emotions
        is_ready = ready_count >= len(recent_sample) / 2
        
        # Additional check: ensure we're not in a sad state
        # (sad is not defensive but also not ready to move forward)
        has_sad = any(state.emotion == EmotionType.SAD for state in recent_sample)
        if has_sad:
            is_ready = False
        
        return is_ready
    
    def get_emotion_history(
        self, 
        window_seconds: Optional[int] = None
    ) -> List[EmotionState]:
        """Get emotion history within a time window.
        
        Args:
            window_seconds: Time window to retrieve (None = all history)
            
        Returns:
            List of emotion states in chronological order
        """
        if window_seconds is None:
            return list(self.emotion_history)
        
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
        return [
            state for state in self.emotion_history
            if state.timestamp >= cutoff_time
        ]
    
    def _cleanup_old_history(self) -> None:
        """Remove emotion states older than the history window."""
        cutoff_time = datetime.now() - self.history_window
        
        while self.emotion_history and self.emotion_history[0].timestamp < cutoff_time:
            self.emotion_history.popleft()
    
    def reset(self) -> None:
        """Reset the detector state and history."""
        self.emotion_history.clear()
        self.pitch_buffer.clear()
        self.energy_buffer.clear()
        self.tempo_buffer.clear()
