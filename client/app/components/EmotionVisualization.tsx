"use client";

import React from "react";
import { Card, CardContent } from "@pipecat-ai/voice-ui-kit";
import { 
  Smile, 
  Frown, 
  Meh, 
  AlertCircle, 
  Shield
} from "lucide-react";

export type EmotionType = 
  | "neutral" 
  | "defensive" 
  | "frustrated" 
  | "sad" 
  | "anxious" 
  | "positive";

interface EmotionVisualizationProps {
  currentEmotion: EmotionType;
  confidence: number; // 0-1
  showLabel?: boolean;
  compact?: boolean;
}

interface EmotionConfig {
  name: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
  description: string;
}

const EMOTION_CONFIGS: Record<EmotionType, EmotionConfig> = {
  neutral: {
    name: "Neutral",
    icon: <Meh className="w-6 h-6" />,
    color: "text-gray-600 dark:text-gray-400",
    bgColor: "bg-gray-100 dark:bg-gray-800",
    description: "Calm and balanced",
  },
  defensive: {
    name: "Defensive",
    icon: <Shield className="w-6 h-6" />,
    color: "text-red-600 dark:text-red-400",
    bgColor: "bg-red-50 dark:bg-red-900/20",
    description: "Protecting against feedback",
  },
  frustrated: {
    name: "Frustrated",
    icon: <AlertCircle className="w-6 h-6" />,
    color: "text-orange-600 dark:text-orange-400",
    bgColor: "bg-orange-50 dark:bg-orange-900/20",
    description: "Feeling challenged",
  },
  sad: {
    name: "Sad",
    icon: <Frown className="w-6 h-6" />,
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-50 dark:bg-blue-900/20",
    description: "Processing difficult emotions",
  },
  anxious: {
    name: "Anxious",
    icon: <AlertCircle className="w-6 h-6" />,
    color: "text-yellow-600 dark:text-yellow-400",
    bgColor: "bg-yellow-50 dark:bg-yellow-900/20",
    description: "Feeling uncertain",
  },
  positive: {
    name: "Positive",
    icon: <Smile className="w-6 h-6" />,
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-50 dark:bg-green-900/20",
    description: "Open and receptive",
  },
};

export const EmotionVisualization: React.FC<EmotionVisualizationProps> = ({
  currentEmotion,
  confidence,
  showLabel = true,
  compact = false,
}) => {
  const [isTransitioning, setIsTransitioning] = React.useState(false);
  const prevEmotionRef = React.useRef<EmotionType>(currentEmotion);

  // Detect emotion changes and trigger animation
  React.useEffect(() => {
    if (prevEmotionRef.current !== currentEmotion) {
      setIsTransitioning(true);
      const timer = setTimeout(() => {
        setIsTransitioning(false);
      }, 300);
      prevEmotionRef.current = currentEmotion;
      return () => clearTimeout(timer);
    }
  }, [currentEmotion]);

  const config = EMOTION_CONFIGS[currentEmotion];
  const confidencePercent = Math.round(confidence * 100);

  if (compact) {
    return (
      <div
        className={`flex items-center gap-2 px-3 py-2 rounded-lg ${config.bgColor} transition-all duration-300 ${
          isTransitioning ? "scale-110" : "scale-100"
        }`}
        title={`${config.name} (${confidencePercent}% confidence)`}
      >
        <div className={`${config.color} transition-colors duration-300`}>
          {config.icon}
        </div>
        {showLabel && (
          <span className={`text-sm font-medium ${config.color}`}>
            {config.name}
          </span>
        )}
      </div>
    );
  }

  return (
    <Card
      className={`transition-all duration-300 ${
        isTransitioning ? "scale-105 shadow-lg" : "scale-100"
      }`}
    >
      <CardContent className={`${config.bgColor} pt-4 pb-4`}>
        <div className="space-y-3">
          {/* Emotion Icon and Label */}
          <div className="flex items-center gap-3">
            <div
              className={`${config.color} transition-all duration-300 ${
                isTransitioning ? "animate-pulse" : ""
              }`}
            >
              {config.icon}
            </div>
            <div className="flex-1 min-w-0">
              {showLabel && (
                <>
                  <h4 className={`text-base font-semibold ${config.color}`}>
                    {config.name}
                  </h4>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                    {config.description}
                  </p>
                </>
              )}
            </div>
          </div>

          {/* Confidence Indicator */}
          {confidence > 0 && (
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
                <span>Confidence</span>
                <span className="font-medium">{confidencePercent}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full ${config.color.replace(
                    "text-",
                    "bg-"
                  )} transition-all duration-500 ease-out`}
                  style={{ width: `${confidencePercent}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
