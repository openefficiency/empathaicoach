"use client";

/**
 * SessionSummary Component
 * 
 * Displays a comprehensive summary of a completed R2C2 coaching session.
 * 
 * Features:
 * - Session duration and phase durations
 * - Emotional journey summary
 * - Key insights and feedback themes discussed
 * - Development plan summary
 * - Next steps and recommendations
 * - Export functionality (PDF/text)
 * 
 * Requirements satisfied:
 * - 7.2: Generate structured summary including emotional reactions, feedback themes, and development plan
 * - 7.4: Display session duration and phase durations
 * - 7.5: Make summary downloadable/shareable
 * 
 * Usage:
 * ```tsx
 * import { SessionSummary } from './components/SessionSummary';
 * 
 * <SessionSummary
 *   sessionId={123}
 *   userId="user-123"
 *   startTime={new Date()}
 *   endTime={new Date()}
 *   phaseDurations={{
 *     relationship: 180,
 *     reaction: 240,
 *     content: 300,
 *     coaching: 360
 *   }}
 *   emotionalJourney={{
 *     startEmotion: "anxious",
 *     endEmotion: "positive",
 *     predominantEmotion: "neutral",
 *     emotionChanges: 8
 *   }}
 *   keyInsights={["Insight 1", "Insight 2"]}
 *   feedbackThemesDiscussed={["Theme 1", "Theme 2"]}
 *   developmentPlan={goals}
 *   nextSteps={["Step 1", "Step 2"]}
 *   onExport={(format) => handleExport(format)}
 * />
 * ```
 */

import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
} from "@pipecat-ai/voice-ui-kit";
import {
  Clock,
  Heart,
  MessageCircle,
  BookOpen,
  Target,
  TrendingUp,
  Download,
  FileText,
  CheckCircle2,
  Lightbulb,
  ArrowRight,
} from "lucide-react";
import { R2C2Phase } from "./R2C2PhaseIndicator";
import { EmotionType } from "./EmotionVisualization";
import { Goal } from "./DevelopmentPlan";
import { exportSession } from "../lib/exportSession";

interface SessionSummaryProps {
  sessionId: number;
  userId: string;
  startTime: Date;
  endTime: Date;
  phaseDurations: Record<R2C2Phase, number>; // seconds
  emotionalJourney: {
    startEmotion: EmotionType;
    endEmotion: EmotionType;
    predominantEmotion: EmotionType;
    emotionChanges: number;
  };
  keyInsights: string[];
  feedbackThemesDiscussed: string[];
  developmentPlan: Goal[];
  nextSteps: string[];
  onExport?: (format: "pdf" | "text") => void;
}

const PHASE_NAMES: Record<R2C2Phase, string> = {
  relationship: "Relationship Building",
  reaction: "Reaction Exploration",
  content: "Content Discussion",
  coaching: "Coaching for Change",
};

const PHASE_ICONS: Record<R2C2Phase, React.ReactNode> = {
  relationship: <Heart className="w-4 h-4" />,
  reaction: <MessageCircle className="w-4 h-4" />,
  content: <BookOpen className="w-4 h-4" />,
  coaching: <Target className="w-4 h-4" />,
};

const EMOTION_LABELS: Record<EmotionType, string> = {
  neutral: "Neutral",
  defensive: "Defensive",
  frustrated: "Frustrated",
  sad: "Sad",
  anxious: "Anxious",
  positive: "Positive",
};

const EMOTION_EMOJIS: Record<EmotionType, string> = {
  neutral: "😐",
  defensive: "🛡️",
  frustrated: "😤",
  sad: "😢",
  anxious: "😰",
  positive: "😊",
};

export const SessionSummary: React.FC<SessionSummaryProps> = ({
  sessionId,
  userId,
  startTime,
  endTime,
  phaseDurations,
  emotionalJourney,
  keyInsights,
  feedbackThemesDiscussed,
  developmentPlan,
  nextSteps,
  onExport,
}) => {
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    if (mins === 0) return `${secs}s`;
    return `${mins}m ${secs}s`;
  };

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const totalDuration = Math.floor(
    (endTime.getTime() - startTime.getTime()) / 1000
  );

  const handleExport = (format: "pdf" | "text") => {
    // Call the custom onExport handler if provided
    if (onExport) {
      onExport(format);
    }
    
    // Use the built-in export functionality
    exportSession(
      {
        sessionId,
        userId,
        startTime,
        endTime,
        phaseDurations,
        emotionalJourney,
        keyInsights,
        feedbackThemesDiscussed,
        developmentPlan,
        nextSteps,
      },
      format
    );
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 p-4">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl mb-2">
                Session Summary
              </CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {formatDate(startTime)} • {formatTime(startTime)} -{" "}
                {formatTime(endTime)}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                Session ID: {sessionId}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport("text")}
                className="flex items-center gap-2"
              >
                <FileText className="w-4 h-4" />
                <span className="hidden sm:inline">Text</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport("pdf")}
                className="flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">PDF</span>
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Session Duration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Clock className="w-5 h-5" />
            Session Duration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="text-center py-4">
              <p className="text-4xl font-bold text-gray-900 dark:text-white">
                {formatDuration(totalDuration)}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Total Session Time
              </p>
            </div>

            {/* Phase Durations */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {(Object.keys(phaseDurations) as R2C2Phase[]).map((phase) => (
                <div
                  key={phase}
                  className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center"
                >
                  <div className="flex justify-center mb-2 text-gray-600 dark:text-gray-400">
                    {PHASE_ICONS[phase]}
                  </div>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {formatDuration(phaseDurations[phase])}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    {PHASE_NAMES[phase].split(" ")[0]}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Emotional Journey */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <TrendingUp className="w-5 h-5" />
            Emotional Journey
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 text-center">
                <p className="text-3xl mb-2">
                  {EMOTION_EMOJIS[emotionalJourney.startEmotion]}
                </p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Started {EMOTION_LABELS[emotionalJourney.startEmotion]}
                </p>
              </div>
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 text-center">
                <p className="text-3xl mb-2">
                  {EMOTION_EMOJIS[emotionalJourney.endEmotion]}
                </p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Ended {EMOTION_LABELS[emotionalJourney.endEmotion]}
                </p>
              </div>
              <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 text-center">
                <p className="text-3xl mb-2">
                  {EMOTION_EMOJIS[emotionalJourney.predominantEmotion]}
                </p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Mostly {EMOTION_LABELS[emotionalJourney.predominantEmotion]}
                </p>
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                You experienced{" "}
                <span className="font-semibold text-gray-900 dark:text-white">
                  {emotionalJourney.emotionChanges} emotional shifts
                </span>{" "}
                during this session, showing your engagement with the feedback
                processing journey.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Insights */}
      {keyInsights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Lightbulb className="w-5 h-5" />
              Key Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {keyInsights.map((insight, index) => (
                <li
                  key={index}
                  className="flex items-start gap-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg"
                >
                  <CheckCircle2 className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-gray-900 dark:text-white">
                    {insight}
                  </p>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Feedback Themes Discussed */}
      {feedbackThemesDiscussed.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <BookOpen className="w-5 h-5" />
              Feedback Themes Discussed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {feedbackThemesDiscussed.map((theme, index) => (
                <span
                  key={index}
                  className="px-3 py-1.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-sm font-medium"
                >
                  {theme}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Development Plan Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Target className="w-5 h-5" />
            Development Plan
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {developmentPlan.length === 0 ? (
              <p className="text-center text-gray-500 dark:text-gray-400 py-4">
                No development plan goals were created during this session.
              </p>
            ) : (
              <>
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                      {
                        developmentPlan.filter((g) => g.goal_type === "start")
                          .length
                      }
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      Start Doing
                    </p>
                  </div>
                  <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                      {
                        developmentPlan.filter((g) => g.goal_type === "stop")
                          .length
                      }
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      Stop Doing
                    </p>
                  </div>
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {
                        developmentPlan.filter(
                          (g) => g.goal_type === "continue"
                        ).length
                      }
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      Continue Doing
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  {developmentPlan.map((goal, index) => (
                    <div
                      key={goal.goal_id}
                      className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-sm font-semibold text-blue-600 dark:text-blue-400">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 dark:text-white mb-1">
                            {goal.goal_text}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {goal.specific_behavior}
                          </p>
                          {goal.target_date && (
                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                              Target: {new Date(goal.target_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Next Steps */}
      {nextSteps.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <ArrowRight className="w-5 h-5" />
              Next Steps
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {nextSteps.map((step, index) => (
                <li
                  key={index}
                  className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-semibold">
                    {index + 1}
                  </div>
                  <p className="text-sm text-gray-900 dark:text-white pt-0.5">
                    {step}
                  </p>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Footer Message */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-200 dark:border-blue-800">
        <CardContent className="pt-6 pb-6">
          <div className="text-center">
            <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Great work on completing your R2C2 coaching session!
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Remember to review your development plan regularly and track your
              progress. You can always come back for another session to continue
              your growth journey.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
