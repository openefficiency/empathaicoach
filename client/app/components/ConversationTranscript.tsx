"use client";

import React, { useEffect, useRef } from "react";
import { EmotionType } from "./EmotionVisualization";
import { TranscriptMessage } from "../hooks/useTranscript";

interface ConversationTranscriptProps {
  messages: TranscriptMessage[];
  assistantLabel?: string;
  clientLabel?: string;
}

const getEmotionIcon = (emotion: EmotionType): string => {
  const emotionIcons: Record<EmotionType, string> = {
    neutral: "😐",
    defensive: "🛡️",
    frustrated: "😤",
    sad: "😢",
    anxious: "😰",
    positive: "😊",
  };
  return emotionIcons[emotion] || "😐";
};

const getEmotionColor = (emotion: EmotionType): string => {
  const emotionColors: Record<EmotionType, string> = {
    neutral: "text-gray-500",
    defensive: "text-orange-500",
    frustrated: "text-red-500",
    sad: "text-blue-500",
    anxious: "text-yellow-500",
    positive: "text-green-500",
  };
  return emotionColors[emotion] || "text-gray-500";
};

const getEmotionBgColor = (emotion: EmotionType): string => {
  const emotionBgColors: Record<EmotionType, string> = {
    neutral: "bg-gray-50 dark:bg-gray-800",
    defensive: "bg-orange-50 dark:bg-orange-900/20",
    frustrated: "bg-red-50 dark:bg-red-900/20",
    sad: "bg-blue-50 dark:bg-blue-900/20",
    anxious: "bg-yellow-50 dark:bg-yellow-900/20",
    positive: "bg-green-50 dark:bg-green-900/20",
  };
  return emotionBgColors[emotion] || "bg-gray-50 dark:bg-gray-800";
};

export const ConversationTranscript: React.FC<ConversationTranscriptProps> = ({
  messages,
  assistantLabel = "Coach",
  clientLabel = "You",
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Transcript messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-400 dark:text-gray-600">
            <div className="text-center">
              <p className="text-lg font-medium mb-2">Conversation will appear here</p>
              <p className="text-sm">Start speaking to begin your R2C2 coaching session</p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.speaker === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 shadow-sm ${
                    message.speaker === "user"
                      ? message.emotion
                        ? getEmotionBgColor(message.emotion)
                        : "bg-blue-100 dark:bg-blue-900/30"
                      : "bg-gray-100 dark:bg-gray-800"
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {message.speaker === "user" && message.emotion && (
                      <span
                        className={`text-xl ${getEmotionColor(message.emotion)}`}
                        title={`Emotion: ${message.emotion}`}
                      >
                        {getEmotionIcon(message.emotion)}
                      </span>
                    )}
                    <div className="flex-1">
                      <div className="text-xs font-semibold mb-1 text-gray-600 dark:text-gray-400">
                        {message.speaker === "user" ? clientLabel : assistantLabel}
                      </div>
                      <div className="text-sm text-gray-900 dark:text-gray-100">
                        {message.text}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
    </div>
  );
};
