"use client";

import { useState, useEffect, useCallback } from "react";
import { DailyEventObjectAppMessage } from "@daily-co/daily-js";
import { EmotionType } from "../components/EmotionVisualization";

export interface TranscriptMessage {
  id: string;
  timestamp: Date;
  speaker: "user" | "assistant";
  text: string;
  emotion?: EmotionType;
}

interface UseTranscriptOptions {
  onAppMessage?: (event: DailyEventObjectAppMessage) => void;
}

export const useTranscript = (options?: UseTranscriptOptions) => {
  const [messages, setMessages] = useState<TranscriptMessage[]>([]);
  const [currentEmotion, setCurrentEmotion] = useState<EmotionType>("neutral");

  const handleAppMessage = useCallback((event: DailyEventObjectAppMessage) => {
    try {
      const data = event.data;

      // Handle emotion detection events
      if (data.type === "emotion-detected") {
        const emotionData = data.data as {
          emotion: EmotionType;
          confidence: number;
        };
        setCurrentEmotion(emotionData.emotion);
      }

      // Handle user transcription
      if (data.type === "user-transcription") {
        const transcriptData = data.data as { text: string };
        if (transcriptData.text && transcriptData.text.trim()) {
          const newMessage: TranscriptMessage = {
            id: `user-${Date.now()}`,
            timestamp: new Date(),
            speaker: "user",
            text: transcriptData.text,
            emotion: currentEmotion,
          };

          setMessages((prev) => {
            // Avoid duplicates
            const lastMessage = prev[prev.length - 1];
            if (
              lastMessage &&
              lastMessage.speaker === "user" &&
              lastMessage.text === transcriptData.text
            ) {
              return prev;
            }
            return [...prev, newMessage];
          });
        }
      }

      // Handle bot TTS text
      if (data.type === "bot-tts-text") {
        const ttsData = data.data as { text: string };
        if (ttsData.text && ttsData.text.trim()) {
          const newMessage: TranscriptMessage = {
            id: `assistant-${Date.now()}`,
            timestamp: new Date(),
            speaker: "assistant",
            text: ttsData.text,
          };

          setMessages((prev) => {
            // Avoid duplicates
            const lastMessage = prev[prev.length - 1];
            if (
              lastMessage &&
              lastMessage.speaker === "assistant" &&
              lastMessage.text === ttsData.text
            ) {
              return prev;
            }
            return [...prev, newMessage];
          });
        }
      }

      // Call custom handler if provided
      options?.onAppMessage?.(event);
    } catch (error) {
      console.error("Error handling app message:", error);
    }
  }, [currentEmotion, options]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentEmotion("neutral");
  }, []);

  return {
    messages,
    currentEmotion,
    handleAppMessage,
    clearMessages,
  };
};
