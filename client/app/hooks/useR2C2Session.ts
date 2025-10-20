"use client";

import { useState, useCallback } from "react";

interface FeedbackTheme {
  category: string;
  theme: string;
  frequency: number;
  examples: string[];
}

interface FeedbackData {
  feedback_id?: string;
  themes: FeedbackTheme[];
  total_comments: number;
}

interface R2C2SessionState {
  userId: string;
  feedbackData: FeedbackData | null;
  sessionId: number | null;
  isSessionActive: boolean;
}

export const useR2C2Session = (initialUserId: string = "default-user") => {
  const [sessionState, setSessionState] = useState<R2C2SessionState>({
    userId: initialUserId,
    feedbackData: null,
    sessionId: null,
    isSessionActive: false,
  });

  const setFeedbackData = useCallback((feedbackData: FeedbackData) => {
    setSessionState((prev) => ({
      ...prev,
      feedbackData,
    }));
  }, []);

  const setUserId = useCallback((userId: string) => {
    setSessionState((prev) => ({
      ...prev,
      userId,
    }));
  }, []);

  const startSession = useCallback((sessionId: number) => {
    setSessionState((prev) => ({
      ...prev,
      sessionId,
      isSessionActive: true,
    }));
  }, []);

  const endSession = useCallback(() => {
    setSessionState((prev) => ({
      ...prev,
      isSessionActive: false,
    }));
  }, []);

  const clearSession = useCallback(() => {
    setSessionState({
      userId: initialUserId,
      feedbackData: null,
      sessionId: null,
      isSessionActive: false,
    });
  }, [initialUserId]);

  const hasFeedbackData = sessionState.feedbackData !== null;

  return {
    sessionState,
    setFeedbackData,
    setUserId,
    startSession,
    endSession,
    clearSession,
    hasFeedbackData,
  };
};
