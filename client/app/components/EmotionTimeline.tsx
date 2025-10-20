"use client";

import React, { useState } from "react";
import { Card, CardContent, Button } from "@pipecat-ai/voice-ui-kit";
import { ChevronDown, ChevronUp, Clock } from "lucide-react";
import { EmotionType } from "./EmotionVisualization";
import { R2C2Phase } from "./R2C2PhaseIndicator";

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

interface EmotionTimelineProps {
  emotions: EmotionEvent[];
  phaseTransitions: PhaseTransition[];
  duration: number; // seconds
  isCollapsed?: boolean;
}

const EMOTION_COLORS: Record<EmotionType, string> = {
  neutral: "#9CA3AF",
  defensive: "#DC2626",
  frustrated: "#EA580C",
  sad: "#2563EB",
  anxious: "#CA8A04",
  positive: "#16A34A",
};

const PHASE_COLORS: Record<R2C2Phase, string> = {
  relationship: "#2563EB",
  reaction: "#9333EA",
  content: "#D97706",
  coaching: "#16A34A",
};

const PHASE_NAMES: Record<R2C2Phase, string> = {
  relationship: "Relationship",
  reaction: "Reaction",
  content: "Content",
  coaching: "Coaching",
};

export const EmotionTimeline: React.FC<EmotionTimelineProps> = ({
  emotions,
  phaseTransitions,
  duration,
  isCollapsed: initialCollapsed = true,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(initialCollapsed);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const getEmotionAtTime = (timeSeconds: number): EmotionType => {
    if (emotions.length === 0) return "neutral";
    
    // Find the most recent emotion before or at this time
    const relevantEmotions = emotions.filter((e) => {
      const emotionTime = (e.timestamp.getTime() - emotions[0].timestamp.getTime()) / 1000;
      return emotionTime <= timeSeconds;
    });
    
    if (relevantEmotions.length === 0) return emotions[0].emotion;
    return relevantEmotions[relevantEmotions.length - 1].emotion;
  };

  const renderTimelineBar = () => {
    if (emotions.length === 0) {
      return (
        <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded-md flex items-center justify-center">
          <span className="text-sm text-gray-500 dark:text-gray-400">
            No emotion data yet
          </span>
        </div>
      );
    }

    const startTime = emotions[0].timestamp.getTime();
    const segments = 100; // Number of segments in the timeline
    const segmentDuration = duration / segments;

    return (
      <div className="relative">
        {/* Timeline bar */}
        <div className="h-12 rounded-md overflow-hidden flex">
          {Array.from({ length: segments }).map((_, index) => {
            const timeSeconds = index * segmentDuration;
            const emotion = getEmotionAtTime(timeSeconds);
            const color = EMOTION_COLORS[emotion];
            
            return (
              <div
                key={index}
                className="flex-1 transition-all duration-200 hover:opacity-80"
                style={{ backgroundColor: color }}
                title={`${formatTime(timeSeconds)} - ${emotion}`}
              />
            );
          })}
        </div>

        {/* Phase transition markers */}
        {phaseTransitions.map((transition, index) => {
          const transitionTime =
            (transition.timestamp.getTime() - startTime) / 1000;
          const position = (transitionTime / duration) * 100;

          return (
            <div
              key={index}
              className="absolute top-0 bottom-0 w-0.5 bg-white dark:bg-gray-900 shadow-md"
              style={{ left: `${position}%` }}
              title={`Phase transition: ${PHASE_NAMES[transition.fromPhase]} → ${PHASE_NAMES[transition.toPhase]}`}
            >
              <div
                className="absolute -top-6 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded text-xs font-medium text-white whitespace-nowrap"
                style={{ backgroundColor: PHASE_COLORS[transition.toPhase] }}
              >
                {PHASE_NAMES[transition.toPhase]}
              </div>
            </div>
          );
        })}

        {/* Time markers */}
        <div className="flex justify-between mt-2 text-xs text-gray-600 dark:text-gray-400">
          <span>{formatTime(0)}</span>
          <span>{formatTime(duration / 2)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>
    );
  };

  const renderEmotionLegend = () => {
    // Get unique emotions from the timeline
    const uniqueEmotions = Array.from(
      new Set(emotions.map((e) => e.emotion))
    ) as EmotionType[];

    if (uniqueEmotions.length === 0) return null;

    return (
      <div className="flex flex-wrap gap-3 mt-4">
        {uniqueEmotions.map((emotion) => (
          <div key={emotion} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: EMOTION_COLORS[emotion] }}
            />
            <span className="text-xs text-gray-600 dark:text-gray-400 capitalize">
              {emotion}
            </span>
          </div>
        ))}
      </div>
    );
  };

  const renderEmotionStats = () => {
    if (emotions.length === 0) return null;

    // Calculate emotion distribution
    const emotionCounts: Record<string, number> = {};
    emotions.forEach((e) => {
      emotionCounts[e.emotion] = (emotionCounts[e.emotion] || 0) + 1;
    });

    const predominantEmotion = Object.entries(emotionCounts).reduce((a, b) =>
      a[1] > b[1] ? a : b
    )[0] as EmotionType;

    const emotionChanges = emotions.filter((e, i) => {
      if (i === 0) return false;
      return e.emotion !== emotions[i - 1].emotion;
    }).length;

    return (
      <div className="grid grid-cols-2 gap-4 mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-md">
        <div>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Predominant Emotion
          </p>
          <p className="text-sm font-medium text-gray-900 dark:text-white capitalize">
            {predominantEmotion}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Emotion Changes
          </p>
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {emotionChanges}
          </p>
        </div>
      </div>
    );
  };

  return (
    <Card>
      <CardContent className="pt-4 pb-4">
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <h3 className="text-base font-semibold text-gray-900 dark:text-white">
                Emotional Journey
              </h3>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="flex items-center gap-1"
            >
              {isCollapsed ? (
                <>
                  <span className="text-sm">Expand</span>
                  <ChevronDown className="w-4 h-4" />
                </>
              ) : (
                <>
                  <span className="text-sm">Collapse</span>
                  <ChevronUp className="w-4 h-4" />
                </>
              )}
            </Button>
          </div>

          {/* Collapsed view - just the timeline bar */}
          {isCollapsed ? (
            <div className="pt-2">{renderTimelineBar()}</div>
          ) : (
            /* Expanded view - timeline + legend + stats */
            <div className="space-y-4 pt-2">
              {renderTimelineBar()}
              {renderEmotionLegend()}
              {renderEmotionStats()}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
