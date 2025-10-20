"""Custom Pipecat processors for R2C2 Voice Coach."""

from .r2c2_processor import R2C2Processor
from .emotion_processor import EmotionProcessor

__all__ = [
    "R2C2Processor",
    "EmotionProcessor",
]
