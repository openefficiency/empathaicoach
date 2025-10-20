"use client";

import React, { useState, useCallback } from "react";
import { Logs, MonitorOff } from "lucide-react";
import Image from "next/image";

// Custom hooks
import { useDailyClient } from "./hooks/useDailyClient";
import { useTranscript } from "./hooks/useTranscript";
import { useR2C2Session } from "./hooks/useR2C2Session";
import { useR2C2PhaseEvents } from "./hooks/useR2C2PhaseEvents";
import { useEmotionEvents } from "./hooks/useEmotionEvents";

// Components
import { Button } from "./components/ui/Button";
import { Card, CardContent } from "./components/ui/Card";
import { AudioControls } from "./components/ui/AudioControls";
import { FeedbackInput } from "./components/FeedbackInput";
import { R2C2PhaseIndicator } from "./components/R2C2PhaseIndicator";
import { EmotionVisualization } from "./components/EmotionVisualization";
import { EmotionTimeline } from "./components/EmotionTimeline";
import { ConversationTranscript } from "./components/ConversationTranscript";
import { FeedbackThemesSidebar } from "./components/FeedbackThemesSidebar";
import { DevelopmentPlan } from "./components/DevelopmentPlan";
import { SessionSummary } from "./components/SessionSummary";
import { EventStreamPanel } from "./EventStreamPanel";

// Types
import { Goal } from "./lib/api";

interface Props {
  isMobile: boolean;
}

export const ClientApp: React.FC<Props> = ({ isMobile }) => {
  // State
  const [hasDisconnected, setHasDisconnected] = useState(false);
  const [showFeedbackInput, setShowFeedbackInput] = useState(true);
  const [showSessionSummary, setShowSessionSummary] = useState(false);
  const [developmentPlanGoals, setDevelopmentPlanGoals] = useState<Goal[]>([]);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  const [sessionEndTime, setSessionEndTime] = useState<Date | null>(null);
  const [showMobileDevelopmentPlan, setShowMobileDevelopmentPlan] = useState(false);
  const [showLogs, setShowLogs] = useState(false);

  // Session management
  const {
    sessionState,
    setFeedbackData,
    endSession,
    hasFeedbackData,
  } = useR2C2Session();

  // Phase and emotion tracking
  const { currentPhase, phaseProgress } = useR2C2PhaseEvents();
  const {
    currentEmotion,
    currentConfidence,
    emotionHistory,
    phaseTransitions,
    sessionDuration,
  } = useEmotionEvents();

  // Transcript management
  const { messages, handleAppMessage, clearMessages } = useTranscript();

  // Daily.co client
  const {
    connectionState,
    isConnected,
    isDisconnected,
    isMicEnabled,
    isCamEnabled,
    isScreenShareEnabled,
    connect,
    disconnect,
    toggleMic,
    toggleCam,
    startScreenShare,
    stopScreenShare,
  } = useDailyClient({
    onAppMessage: handleAppMessage,
    onDisconnect: () => {
      setSessionEndTime(new Date());
      setHasDisconnected(true);
      setShowSessionSummary(true);
      endSession();
    },
  });

  // Handlers
  const handleFeedbackSubmit = useCallback((feedbackData: unknown) => {
    setFeedbackData(feedbackData as any);
  }, [setFeedbackData]);

  const handleContinueToSession = useCallback(() => {
    setShowFeedbackInput(false);
  }, []);

  const handleConnect = useCallback(async () => {
    try {
      setSessionStartTime(new Date());
      setShowSessionSummary(false);
      clearMessages();

      // Call the Next.js API route which proxies to the backend bot starter
      // The API route forwards the request to the backend at /start
      const response = await fetch("/api/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          feedback_data: sessionState.feedbackData,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Start session response:", errorText);
        throw new Error(`Failed to start session: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log("Bot starter response:", data);
      
      // Handle both response formats: {dailyRoom, dailyToken} or {room_url, token}
      const roomUrl = data.dailyRoom || data.room_url;
      const token = data.dailyToken || data.token;
      
      // Validate response data
      if (!roomUrl || typeof roomUrl !== 'string') {
        throw new Error(`Invalid room URL in response: ${JSON.stringify(data)}`);
      }
      
      console.log("Connecting to Daily room:", roomUrl);
      
      // Connect to Daily.co room
      await connect(roomUrl, token);
    } catch (error) {
      console.error("Connection error:", error);
      // Show error to user
      alert(`Failed to connect: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [sessionState.feedbackData, connect, clearMessages]);

  const handleDisconnect = useCallback(async () => {
    await disconnect();
  }, [disconnect]);

  const handleGoalComplete = useCallback((goalId: number, completedAt: string) => {
    setDevelopmentPlanGoals((prevGoals) =>
      prevGoals.map((goal) =>
        goal.goal_id === goalId
          ? { ...goal, is_completed: true, completed_at: completedAt }
          : goal
      )
    );
  }, []);

  const handleGoalUpdate = useCallback((updatedGoal: Goal) => {
    setDevelopmentPlanGoals((prevGoals) =>
      prevGoals.map((goal) =>
        goal.goal_id === updatedGoal.goal_id ? updatedGoal : goal
      )
    );
  }, []);

  const handleNewSession = useCallback(() => {
    setHasDisconnected(false);
    setShowSessionSummary(false);
    setShowFeedbackInput(true);
    setDevelopmentPlanGoals([]);
    setSessionStartTime(null);
    setSessionEndTime(null);
    clearMessages();
  }, [clearMessages]);

  const handleToggleLogs = useCallback(() => {
    setShowLogs((prev) => !prev);
  }, []);

  const handleToggleScreenShare = useCallback(() => {
    if (isScreenShareEnabled) {
      stopScreenShare();
    } else {
      startScreenShare();
    }
  }, [isScreenShareEnabled, stopScreenShare, startScreenShare]);

  return (
    <div
      className="min-h-screen bg-gray-50 dark:bg-gray-900"
      style={
        {
          "--controls-height": "144px",
          "--header-height": "97px",
          "--phase-indicator-height": "120px",
        } as React.CSSProperties
      }
    >
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            <div className="flex items-center gap-2 sm:gap-4">
              <Image 
                src="/pipecat.svg" 
                alt="R2C2 Voice Coach" 
                width={isMobile ? 24 : 32} 
                height={isMobile ? 24 : 32} 
              />
              <h1 className="text-base sm:text-xl font-semibold text-gray-900 dark:text-white">
                R2C2 Voice Coach
              </h1>
            </div>
            {!hasDisconnected && !showFeedbackInput && (
              <div className="flex items-center gap-2 sm:gap-4">
                {isDisconnected && !isMobile && (
                  <Button
                    variant="outline"
                    onClick={() => setShowFeedbackInput(true)}
                    size="sm"
                  >
                    Back to Feedback
                  </Button>
                )}
                <Button
                  variant={isConnected ? "outline" : "primary"}
                  onClick={isConnected ? handleDisconnect : handleConnect}
                  size="sm"
                  disabled={connectionState === "connecting"}
                >
                  {connectionState === "connecting" ? "Connecting..." : isConnected ? "Disconnect" : "Connect"}
                </Button>
                {!isMobile && (
                  <Button
                    variant={showLogs ? "primary" : "outline"}
                    onClick={handleToggleLogs}
                    title={showLogs ? "Hide logs" : "Show logs"}
                    size="sm"
                  >
                    <Logs />
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      {hasDisconnected && showSessionSummary ? (
        <main className="relative max-w-7xl mx-auto mt-4 sm:mt-8 px-3 sm:px-4 pb-6 sm:pb-8 overflow-y-auto">
          <SessionSummary
            sessionId={sessionState.sessionId || 0}
            userId={sessionState.userId}
            startTime={sessionStartTime || new Date()}
            endTime={sessionEndTime || new Date()}
            phaseDurations={{
              relationship: 0,
              reaction: 0,
              content: 0,
              coaching: 0,
            }}
            emotionalJourney={{
              startEmotion: emotionHistory[0]?.emotion || "neutral",
              endEmotion: emotionHistory[emotionHistory.length - 1]?.emotion || "neutral",
              predominantEmotion: currentEmotion,
              emotionChanges: phaseTransitions.length,
            }}
            keyInsights={[
              "You successfully processed your 360° feedback",
              "You created a concrete development plan with actionable goals",
            ]}
            feedbackThemesDiscussed={
              sessionState.feedbackData?.themes.map((t) => t.theme) || []
            }
            developmentPlan={developmentPlanGoals}
            nextSteps={[
              "Review your development plan regularly",
              "Share your commitments with your manager or mentor",
              "Schedule a follow-up session to track progress",
            ]}
            onExport={(format) => {
              console.log(`Exporting session in ${format} format`);
            }}
          />
          <div className="mt-6 sm:mt-8 flex justify-center">
            <Button onClick={handleNewSession} size="lg" className="w-full sm:w-auto">
              Start New Session
            </Button>
          </div>
        </main>
      ) : showFeedbackInput ? (
        <main className="relative max-w-7xl mx-auto mt-4 sm:mt-8 px-3 sm:px-4 py-4 sm:py-8">
          <div className="mb-4 sm:mb-6">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Welcome to R2C2 Voice Coach
            </h2>
            <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
              Let&apos;s start by uploading your 360° feedback data. This will help me guide you through processing your feedback effectively.
            </p>
          </div>
          
          <FeedbackInput
            onFeedbackSubmit={handleFeedbackSubmit}
            userId={sessionState.userId}
          />
          
          {hasFeedbackData && (
            <div className="mt-6 sm:mt-8 space-y-4">
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3 sm:p-4">
                <p className="text-sm sm:text-base text-green-800 dark:text-green-200 font-medium">
                  ✓ Feedback data loaded successfully
                </p>
                <p className="text-xs sm:text-sm text-green-700 dark:text-green-300 mt-1">
                  {sessionState.feedbackData?.themes.length || 0} themes identified from {sessionState.feedbackData?.total_comments || 0} comments
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4">
                <Button
                  variant="outline"
                  onClick={() => {
                    setFeedbackData(null as any);
                  }}
                  className="w-full sm:w-auto"
                >
                  Change Feedback
                </Button>
                <Button
                  onClick={handleContinueToSession}
                  size="lg"
                  className="w-full sm:w-auto"
                >
                  Continue to Session
                </Button>
              </div>
            </div>
          )}
        </main>
      ) : (
        <main className="relative max-w-7xl mx-auto mt-2 sm:mt-8 px-2 sm:px-4 overflow-hidden">
          {/* R2C2 Phase Indicator */}
          {!isDisconnected && (
            <div className="mb-2 sm:mb-4">
              <R2C2PhaseIndicator
                currentPhase={currentPhase}
                phaseProgress={phaseProgress}
                showDescription={!isMobile}
              />
            </div>
          )}
          
          {/* Main conversation area */}
          <div className="h-[calc(100vh-var(--header-height)-var(--controls-height)-var(--phase-indicator-height))]">
            <div className="h-full flex flex-col lg:flex-row gap-4">
              {/* Left sidebar - Emotion visualization (desktop only) */}
              {!isMobile && (
                <div className="w-full lg:w-64 space-y-4">
                  <EmotionVisualization
                    currentEmotion={currentEmotion}
                    confidence={currentConfidence}
                    showLabel={true}
                  />
                  <EmotionTimeline
                    emotions={emotionHistory}
                    phaseTransitions={phaseTransitions}
                    duration={sessionDuration}
                    isCollapsed={false}
                  />
                </div>
              )}

              {/* Center - Conversation */}
              <div className="flex-1 flex flex-col gap-4">
                {/* Mobile emotion viz */}
                {isMobile && (
                  <div className="h-20">
                    <EmotionVisualization
                      currentEmotion={currentEmotion}
                      confidence={currentConfidence}
                      showLabel={false}
                    />
                  </div>
                )}

                {/* Conversation transcript */}
                <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                  <div className="h-full flex flex-col">
                    <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900 dark:text-white">Conversation</h3>
                      {isMobile && currentPhase === "coaching" && developmentPlanGoals.length > 0 && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowMobileDevelopmentPlan(!showMobileDevelopmentPlan)}
                        >
                          {showMobileDevelopmentPlan ? "Back to Chat" : "View Plan"}
                        </Button>
                      )}
                    </div>
                    <div className="flex-1 overflow-hidden">
                      {showMobileDevelopmentPlan && isMobile ? (
                        <div className="h-full overflow-y-auto p-4">
                          <DevelopmentPlan
                            goals={developmentPlanGoals}
                            onGoalComplete={handleGoalComplete}
                            editable={currentPhase === "coaching"}
                            onGoalUpdate={handleGoalUpdate}
                          />
                        </div>
                      ) : (
                        <ConversationTranscript
                          messages={messages}
                          assistantLabel="Coach"
                          clientLabel="You"
                        />
                      )}
                    </div>
                  </div>
                </div>

                {/* Development plan (desktop, during coaching phase) */}
                {!isMobile && currentPhase === "coaching" && developmentPlanGoals.length > 0 && (
                  <div className="h-64 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-y-auto p-4">
                    <DevelopmentPlan
                      goals={developmentPlanGoals}
                      onGoalComplete={handleGoalComplete}
                      editable={currentPhase === "coaching"}
                      onGoalUpdate={handleGoalUpdate}
                    />
                  </div>
                )}
              </div>

              {/* Right sidebar - Feedback themes (desktop only) */}
              {!isMobile && hasFeedbackData && sessionState.feedbackData?.themes && !isScreenShareEnabled && (
                <div className="w-full lg:w-80">
                  <FeedbackThemesSidebar
                    themes={sessionState.feedbackData.themes}
                    discussedThemes={[]}
                  />
                </div>
              )}
            </div>

            {/* Event logs (if enabled) */}
            {showLogs && !isMobile && (
              <div className="mt-4 h-64">
                <EventStreamPanel />
              </div>
            )}
          </div>

          {/* Audio controls */}
          <div className="fixed bottom-4 sm:bottom-8 left-1/2 -translate-x-1/2 z-10">
            <Card className="shadow-lg">
              <CardContent className="flex items-center justify-center gap-1 sm:gap-2 p-2 sm:p-4">
                <AudioControls
                  isMicEnabled={isMicEnabled}
                  isCamEnabled={isCamEnabled}
                  isScreenShareEnabled={isScreenShareEnabled}
                  onToggleMic={toggleMic}
                  onToggleCam={toggleCam}
                  onToggleScreenShare={handleToggleScreenShare}
                  showVideo={!isMobile}
                  showScreenShare={!isMobile}
                />
              </CardContent>
            </Card>
          </div>

          {/* Mobile screen share notice */}
          {isMobile && (
            <div className="mt-8">
              <Card className="border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20">
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-2 text-yellow-800 dark:text-yellow-200">
                    <MonitorOff className="h-5 w-5" />
                    <p className="font-medium">
                      Screen sharing is not available on mobile devices
                    </p>
                  </div>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                    Please use a desktop browser to access screen sharing features.
                  </p>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      )}
    </div>
  );
};
