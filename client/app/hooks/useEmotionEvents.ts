"use client";

import { useEffect, useState } from "react";
import { usePipecatEventStream } from "@pipecat-ai/voice-ui-kit";
import { EmotionType } from "../components/EmotionVisualization";
import { R2C2Phase } from "../components/R2C2PhaseIndicator";

interface EmotionEventData {
  emotion: EmotionType;
  confidence: number;
  timestamp: string;
  phase?: R2C2Phase;
}

interface EmotionEvent {
  timestamp: Date;
  emotion: EmotionType;
  confidence: number;
  phase: R2C2Phase;
}

interface PhaseTransition {
  fromPhase: R2C2Phase;
  toPhase: R2C2Phase;
  timestamp: Date;
}

interface EmotionState {
  currentEmotion: EmotionType;
  currentConfidence: number;
  emotionHistory: EmotionEvent[];
  phaseTransitions: PhaseTransition[];
  sessionStartTime: Date | null;
}

export const useEmotionEvents = () => {
  const { events } = usePipecatEventStream({
    maxEvents: 1000,
    ignoreEvents: [],
  });

  const [emotionState, setEmotionState] = useState<EmotionState>({
    currentEmotion: "neutral",
    currentConfidence: 0,
    emotionHistory: [],
    phaseTransitions: [],
    sessionStartTime: null,
  });

  // Listen for emotion events from the backend
  useEffect(() => {
    if (events.length === 0) return;

    // Get the most recent event
    const latestEvent = events[events.length - 1];

    try {
      // Check if this is an emotion detection event
      if (latestEvent.type === "emotion-detected" && latestEvent.data) {
        const emotionData = latestEvent.data as EmotionEventData;

        console.log("Emotion detected:", emotionData);

        const emotionEvent: EmotionEvent = {
          timestamp: new Date(emotionData.timestamp),
          emotion: emotionData.emotion,
          confidence: emotionData.confidence,
          phase: emotionData.phase || "relationship",
        };

        setEmotionState((prev) => {
          // Initialize session start time if not set
          const sessionStartTime = prev.sessionStartTime || new Date();

          // Add to history
          const updatedHistory = [...prev.emotionHistory, emotionEvent];

          return {
            ...prev,
            currentEmotion: emotionData.emotion,
            currentConfidence: emotionData.confidence,
            emotionHistory: updatedHistory,
            sessionStartTime,
          };
        });
      }

      // Check if this is a phase transition event
      if (latestEvent.type === "r2c2-phase-transition" && latestEvent.data) {
        const transitionData = latestEvent.data as {
          from_phase: R2C2Phase;
          to_phase: R2C2Phase;
          timestamp: string;
        };

        console.log("Phase transition detected:", transitionData);

        const phaseTransition: PhaseTransition = {
          fromPhase: transitionData.from_phase,
          toPhase: transitionData.to_phase,
          timestamp: new Date(transitionData.timestamp),
        };

        setEmotionState((prev) => ({
          ...prev,
          phaseTransitions: [...prev.phaseTransitions, phaseTransition],
        }));
      }
    } catch (error) {
      console.error("Error handling emotion/phase event:", error);
    }
  }, [events]);

  // Calculate session duration
  const getSessionDuration = (): number => {
    if (!emotionState.sessionStartTime) return 0;
    const now = new Date();
    return (now.getTime() - emotionState.sessionStartTime.getTime()) / 1000;
  };

  // Get emotion trend over a time window
  const getEmotionTrend = (windowSeconds: number = 30): EmotionType => {
    if (emotionState.emotionHistory.length === 0) return "neutral";

    const now = new Date();
    const windowStart = new Date(now.getTime() - windowSeconds * 1000);

    const recentEmotions = emotionState.emotionHistory.filter(
      (e) => e.timestamp >= windowStart
    );

    if (recentEmotions.length === 0) {
      return emotionState.emotionHistory[emotionState.emotionHistory.length - 1]
        .emotion;
    }

    // Count occurrences of each emotion
    const emotionCounts: Record<string, number> = {};
    recentEmotions.forEach((e) => {
      emotionCounts[e.emotion] = (emotionCounts[e.emotion] || 0) + 1;
    });

    // Return the most frequent emotion
    const predominantEmotion = Object.entries(emotionCounts).reduce((a, b) =>
      a[1] > b[1] ? a : b
    )[0] as EmotionType;

    return predominantEmotion;
  };

  // Check if emotion is improving (moving toward positive/neutral)
  const isEmotionImproving = (): boolean => {
    if (emotionState.emotionHistory.length < 2) return false;

    const recentEmotions = emotionState.emotionHistory.slice(-5);
    const negativeEmotions: EmotionType[] = [
      "defensive",
      "frustrated",
      "sad",
      "anxious",
    ];

    let negativeCount = 0;
    recentEmotions.forEach((e) => {
      if (negativeEmotions.includes(e.emotion)) {
        negativeCount++;
      }
    });

    // Emotion is improving if less than half of recent emotions are negative
    return negativeCount < recentEmotions.length / 2;
  };

  // Reset emotion state (for new session)
  const resetEmotionState = () => {
    setEmotionState({
      currentEmotion: "neutral",
      currentConfidence: 0,
      emotionHistory: [],
      phaseTransitions: [],
      sessionStartTime: null,
    });
  };

  return {
    currentEmotion: emotionState.currentEmotion,
    currentConfidence: emotionState.currentConfidence,
    emotionHistory: emotionState.emotionHistory,
    phaseTransitions: emotionState.phaseTransitions,
    sessionDuration: getSessionDuration(),
    getEmotionTrend,
    isEmotionImproving,
    resetEmotionState,
  };
};
