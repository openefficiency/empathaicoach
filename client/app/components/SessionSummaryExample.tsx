/**
 * Example usage of SessionSummary component
 * 
 * This file demonstrates how to integrate the SessionSummary component
 * into your application after a coaching session completes.
 */

"use client";

import React from "react";
import { SessionSummary } from "./SessionSummary";
import { Goal } from "./DevelopmentPlan";

export function SessionSummaryExample() {
  // Example session data
  const sessionId = 123;
  const userId = "user-123";
  const startTime = new Date("2025-10-17T10:00:00");
  const endTime = new Date("2025-10-17T10:18:00");

  const phaseDurations = {
    relationship: 180, // 3 minutes
    reaction: 240, // 4 minutes
    content: 300, // 5 minutes
    coaching: 360, // 6 minutes
  };

  const emotionalJourney = {
    startEmotion: "anxious" as const,
    endEmotion: "positive" as const,
    predominantEmotion: "neutral" as const,
    emotionChanges: 8,
  };

  const keyInsights = [
    "You showed great openness to feedback about communication style",
    "Recognized the pattern of interrupting team members during meetings",
    "Identified that stress management affects your leadership presence",
    "Acknowledged the positive impact of your technical mentorship",
  ];

  const feedbackThemesDiscussed = [
    "Communication Style",
    "Active Listening",
    "Team Collaboration",
    "Technical Leadership",
    "Stress Management",
  ];

  const developmentPlan: Goal[] = [
    {
      goal_id: 1,
      goal_text: "Practice active listening in team meetings",
      goal_type: "start",
      specific_behavior:
        "Wait 3 seconds after someone finishes speaking before responding",
      measurable_criteria:
        "Receive positive feedback from at least 3 team members within 30 days",
      target_date: "2025-11-17",
      action_steps: [
        "Set a reminder before each meeting to focus on listening",
        "Take notes during conversations to stay engaged",
        "Ask clarifying questions instead of jumping to solutions",
      ],
      is_completed: false,
    },
    {
      goal_id: 2,
      goal_text: "Stop checking phone during one-on-ones",
      goal_type: "stop",
      specific_behavior:
        "Keep phone in drawer or bag during all scheduled one-on-one meetings",
      measurable_criteria: "Zero phone checks during one-on-ones for 4 weeks",
      target_date: "2025-11-17",
      action_steps: [
        "Set phone to Do Not Disturb mode before meetings",
        "Use a notebook instead of phone for note-taking",
        "Schedule buffer time before meetings to handle urgent items",
      ],
      is_completed: false,
    },
    {
      goal_id: 3,
      goal_text: "Continue weekly technical mentorship sessions",
      goal_type: "continue",
      specific_behavior:
        "Maintain current schedule of 1-hour mentorship sessions with junior developers",
      measurable_criteria:
        "Complete 12 consecutive weekly sessions with documented progress",
      target_date: "2026-01-17",
      action_steps: [
        "Block calendar time every Friday afternoon",
        "Prepare session topics in advance",
        "Follow up with mentees on their progress",
      ],
      is_completed: false,
    },
  ];

  const nextSteps = [
    "Share your development plan with your manager within 48 hours",
    "Schedule a 30-day check-in to review progress on your goals",
    "Join the company's active listening workshop next month",
    "Set up weekly reminders to review your action steps",
    "Consider finding an accountability partner for your goals",
  ];

  const handleExport = (format: "pdf" | "text") => {
    console.log(`Exporting session summary as ${format}`);
    // The SessionSummary component handles the actual export
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <SessionSummary
        sessionId={sessionId}
        userId={userId}
        startTime={startTime}
        endTime={endTime}
        phaseDurations={phaseDurations}
        emotionalJourney={emotionalJourney}
        keyInsights={keyInsights}
        feedbackThemesDiscussed={feedbackThemesDiscussed}
        developmentPlan={developmentPlan}
        nextSteps={nextSteps}
        onExport={handleExport}
      />
    </div>
  );
}
