/**
 * Session Export Utilities
 * 
 * Provides functionality to export session summaries in various formats (PDF, text).
 * 
 * Requirements satisfied:
 * - 7.5: Make summary downloadable/shareable in professional format
 */

import { R2C2Phase } from "../components/R2C2PhaseIndicator";
import { EmotionType } from "../components/EmotionVisualization";
import { Goal } from "../components/DevelopmentPlan";

interface SessionExportData {
  sessionId: number;
  userId: string;
  startTime: Date;
  endTime: Date;
  phaseDurations: Record<R2C2Phase, number>;
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
  transcript?: Array<{
    timestamp: Date;
    speaker: "user" | "assistant";
    text: string;
    emotion?: EmotionType;
  }>;
}

const PHASE_NAMES: Record<R2C2Phase, string> = {
  relationship: "Relationship Building",
  reaction: "Reaction Exploration",
  content: "Content Discussion",
  coaching: "Coaching for Change",
};

const EMOTION_LABELS: Record<EmotionType, string> = {
  neutral: "Neutral",
  defensive: "Defensive",
  frustrated: "Frustrated",
  sad: "Sad",
  anxious: "Anxious",
  positive: "Positive",
};

/**
 * Format duration in seconds to human-readable string
 */
function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  if (mins === 0) return `${secs} seconds`;
  if (secs === 0) return `${mins} minutes`;
  return `${mins} minutes ${secs} seconds`;
}

/**
 * Format date to readable string
 */
function formatDate(date: Date): string {
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/**
 * Format time to readable string
 */
function formatTime(date: Date): string {
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Generate text content for session summary
 */
function generateTextContent(data: SessionExportData): string {
  const totalDuration = Math.floor(
    (data.endTime.getTime() - data.startTime.getTime()) / 1000
  );

  let content = "";

  // Header
  content += "═══════════════════════════════════════════════════════════\n";
  content += "           R2C2 VOICE COACH - SESSION SUMMARY\n";
  content += "═══════════════════════════════════════════════════════════\n\n";

  // Session Info
  content += `Session ID: ${data.sessionId}\n`;
  content += `User ID: ${data.userId}\n`;
  content += `Date: ${formatDate(data.startTime)}\n`;
  content += `Time: ${formatTime(data.startTime)} - ${formatTime(data.endTime)}\n`;
  content += `Total Duration: ${formatDuration(totalDuration)}\n\n`;

  // Session Duration by Phase
  content += "───────────────────────────────────────────────────────────\n";
  content += "SESSION DURATION BY PHASE\n";
  content += "───────────────────────────────────────────────────────────\n\n";
  (Object.keys(data.phaseDurations) as R2C2Phase[]).forEach((phase) => {
    content += `${PHASE_NAMES[phase]}: ${formatDuration(
      data.phaseDurations[phase]
    )}\n`;
  });
  content += "\n";

  // Emotional Journey
  content += "───────────────────────────────────────────────────────────\n";
  content += "EMOTIONAL JOURNEY\n";
  content += "───────────────────────────────────────────────────────────\n\n";
  content += `Starting Emotion: ${
    EMOTION_LABELS[data.emotionalJourney.startEmotion]
  }\n`;
  content += `Ending Emotion: ${
    EMOTION_LABELS[data.emotionalJourney.endEmotion]
  }\n`;
  content += `Predominant Emotion: ${
    EMOTION_LABELS[data.emotionalJourney.predominantEmotion]
  }\n`;
  content += `Emotional Shifts: ${data.emotionalJourney.emotionChanges}\n\n`;

  // Key Insights
  if (data.keyInsights.length > 0) {
    content += "───────────────────────────────────────────────────────────\n";
    content += "KEY INSIGHTS\n";
    content += "───────────────────────────────────────────────────────────\n\n";
    data.keyInsights.forEach((insight, idx) => {
      content += `${idx + 1}. ${insight}\n\n`;
    });
  }

  // Feedback Themes
  if (data.feedbackThemesDiscussed.length > 0) {
    content += "───────────────────────────────────────────────────────────\n";
    content += "FEEDBACK THEMES DISCUSSED\n";
    content += "───────────────────────────────────────────────────────────\n\n";
    data.feedbackThemesDiscussed.forEach((theme, index) => {
      content += `• ${theme}\n`;
    });
    content += "\n";
  }

  // Development Plan
  content += "───────────────────────────────────────────────────────────\n";
  content += "DEVELOPMENT PLAN\n";
  content += "───────────────────────────────────────────────────────────\n\n";

  if (data.developmentPlan.length === 0) {
    content += "No development plan goals were created during this session.\n\n";
  } else {
    data.developmentPlan.forEach((goal, index) => {
      content += `Goal ${index + 1}: ${goal.goal_text}\n`;
      content += `Type: ${goal.goal_type.toUpperCase()}\n`;
      content += `Specific Behavior: ${goal.specific_behavior}\n`;
      content += `Success Criteria: ${goal.measurable_criteria}\n`;
      if (goal.target_date) {
        content += `Target Date: ${new Date(goal.target_date).toLocaleDateString()}\n`;
      }
      if (goal.action_steps.length > 0) {
        content += `Action Steps:\n`;
        goal.action_steps.forEach((step) => {
          content += `  • ${step}\n`;
        });
      }
      content += "\n";
    });
  }

  // Next Steps
  if (data.nextSteps.length > 0) {
    content += "───────────────────────────────────────────────────────────\n";
    content += "NEXT STEPS\n";
    content += "───────────────────────────────────────────────────────────\n\n";
    data.nextSteps.forEach((step, index) => {
      content += `${index + 1}. ${step}\n`;
    });
    content += "\n";
  }

  // Transcript (if provided)
  if (data.transcript && data.transcript.length > 0) {
    content += "───────────────────────────────────────────────────────────\n";
    content += "CONVERSATION TRANSCRIPT\n";
    content += "───────────────────────────────────────────────────────────\n\n";
    data.transcript.forEach((entry) => {
      const speaker = entry.speaker === "user" ? "You" : "Coach";
      const emotion = entry.emotion ? ` [${EMOTION_LABELS[entry.emotion]}]` : "";
      content += `[${formatTime(entry.timestamp)}] ${speaker}${emotion}:\n`;
      content += `${entry.text}\n\n`;
    });
  }

  // Footer
  content += "═══════════════════════════════════════════════════════════\n";
  content += "Generated by R2C2 Voice Coach\n";
  content += `Export Date: ${formatDate(new Date())}\n`;
  content += "═══════════════════════════════════════════════════════════\n";

  return content;
}

/**
 * Export session summary as text file
 */
export function exportAsText(data: SessionExportData): void {
  const content = generateTextContent(data);
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `r2c2-session-${data.sessionId}-${formatDate(
    data.startTime
  ).replace(/\s/g, "-")}.txt`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Generate HTML content for PDF export
 */
function generateHTMLContent(data: SessionExportData): string {
  const totalDuration = Math.floor(
    (data.endTime.getTime() - data.startTime.getTime()) / 1000
  );

  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>R2C2 Session Summary - ${data.sessionId}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px 20px;
    }
    .header {
      text-align: center;
      border-bottom: 3px solid #2563eb;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .header h1 {
      color: #2563eb;
      margin: 0 0 10px 0;
      font-size: 28px;
    }
    .header .subtitle {
      color: #6b7280;
      font-size: 14px;
    }
    .section {
      margin-bottom: 30px;
      page-break-inside: avoid;
    }
    .section-title {
      color: #1f2937;
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 15px;
      padding-bottom: 8px;
      border-bottom: 2px solid #e5e7eb;
    }
    .info-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 15px;
      margin-bottom: 20px;
    }
    .info-item {
      background: #f9fafb;
      padding: 12px;
      border-radius: 6px;
    }
    .info-label {
      font-size: 12px;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }
    .info-value {
      font-size: 16px;
      font-weight: 600;
      color: #1f2937;
    }
    .emotion-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 15px;
      margin-bottom: 15px;
    }
    .emotion-card {
      background: #f0f9ff;
      padding: 15px;
      border-radius: 8px;
      text-align: center;
    }
    .emotion-emoji {
      font-size: 32px;
      margin-bottom: 8px;
    }
    .emotion-label {
      font-size: 14px;
      font-weight: 500;
      color: #1f2937;
    }
    .insight-list, .theme-list, .step-list {
      list-style: none;
      padding: 0;
    }
    .insight-item, .step-item {
      background: #fffbeb;
      padding: 12px 15px;
      margin-bottom: 10px;
      border-radius: 6px;
      border-left: 4px solid #f59e0b;
    }
    .theme-tag {
      display: inline-block;
      background: #dbeafe;
      color: #1e40af;
      padding: 6px 12px;
      border-radius: 20px;
      margin: 4px;
      font-size: 14px;
    }
    .goal {
      background: #f9fafb;
      padding: 15px;
      margin-bottom: 15px;
      border-radius: 8px;
      border-left: 4px solid #2563eb;
    }
    .goal-header {
      font-weight: 600;
      color: #1f2937;
      margin-bottom: 8px;
      font-size: 16px;
    }
    .goal-type {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      margin-bottom: 8px;
    }
    .goal-type-start { background: #d1fae5; color: #065f46; }
    .goal-type-stop { background: #fee2e2; color: #991b1b; }
    .goal-type-continue { background: #dbeafe; color: #1e40af; }
    .goal-detail {
      font-size: 14px;
      color: #4b5563;
      margin-bottom: 6px;
    }
    .goal-detail strong {
      color: #1f2937;
    }
    .action-steps {
      margin-top: 8px;
      padding-left: 20px;
    }
    .action-steps li {
      font-size: 14px;
      color: #4b5563;
      margin-bottom: 4px;
    }
    .footer {
      text-align: center;
      margin-top: 40px;
      padding-top: 20px;
      border-top: 2px solid #e5e7eb;
      color: #6b7280;
      font-size: 12px;
    }
    @media print {
      body { padding: 20px; }
      .section { page-break-inside: avoid; }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>R2C2 Voice Coach Session Summary</h1>
    <div class="subtitle">
      ${formatDate(data.startTime)} • ${formatTime(data.startTime)} - ${formatTime(
    data.endTime
  )}
    </div>
    <div class="subtitle">Session ID: ${data.sessionId}</div>
  </div>

  <div class="section">
    <div class="section-title">Session Overview</div>
    <div class="info-grid">
      <div class="info-item">
        <div class="info-label">Total Duration</div>
        <div class="info-value">${formatDuration(totalDuration)}</div>
      </div>
      <div class="info-item">
        <div class="info-label">Emotional Shifts</div>
        <div class="info-value">${data.emotionalJourney.emotionChanges}</div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Phase Durations</div>
    <div class="info-grid">
      ${(Object.keys(data.phaseDurations) as R2C2Phase[])
        .map(
          (phase) => `
        <div class="info-item">
          <div class="info-label">${PHASE_NAMES[phase]}</div>
          <div class="info-value">${formatDuration(
            data.phaseDurations[phase]
          )}</div>
        </div>
      `
        )
        .join("")}
    </div>
  </div>

  <div class="section">
    <div class="section-title">Emotional Journey</div>
    <div class="emotion-grid">
      <div class="emotion-card">
        <div class="emotion-emoji">😰</div>
        <div class="emotion-label">Started ${
          EMOTION_LABELS[data.emotionalJourney.startEmotion]
        }</div>
      </div>
      <div class="emotion-card">
        <div class="emotion-emoji">😊</div>
        <div class="emotion-label">Ended ${
          EMOTION_LABELS[data.emotionalJourney.endEmotion]
        }</div>
      </div>
      <div class="emotion-card">
        <div class="emotion-emoji">😐</div>
        <div class="emotion-label">Mostly ${
          EMOTION_LABELS[data.emotionalJourney.predominantEmotion]
        }</div>
      </div>
    </div>
  </div>

  ${
    data.keyInsights.length > 0
      ? `
  <div class="section">
    <div class="section-title">Key Insights</div>
    <ul class="insight-list">
      ${data.keyInsights
        .map(
          (insight) => `
        <li class="insight-item">${insight}</li>
      `
        )
        .join("")}
    </ul>
  </div>
  `
      : ""
  }

  ${
    data.feedbackThemesDiscussed.length > 0
      ? `
  <div class="section">
    <div class="section-title">Feedback Themes Discussed</div>
    <div>
      ${data.feedbackThemesDiscussed
        .map((theme) => `<span class="theme-tag">${theme}</span>`)
        .join("")}
    </div>
  </div>
  `
      : ""
  }

  <div class="section">
    <div class="section-title">Development Plan</div>
    ${
      data.developmentPlan.length === 0
        ? '<p style="color: #6b7280;">No development plan goals were created during this session.</p>'
        : data.developmentPlan
            .map(
              (goal) => `
      <div class="goal">
        <div class="goal-type goal-type-${goal.goal_type}">${goal.goal_type}</div>
        <div class="goal-header">${goal.goal_text}</div>
        <div class="goal-detail"><strong>Specific Behavior:</strong> ${
          goal.specific_behavior
        }</div>
        <div class="goal-detail"><strong>Success Criteria:</strong> ${
          goal.measurable_criteria
        }</div>
        ${
          goal.target_date
            ? `<div class="goal-detail"><strong>Target Date:</strong> ${new Date(
                goal.target_date
              ).toLocaleDateString()}</div>`
            : ""
        }
        ${
          goal.action_steps.length > 0
            ? `
          <div class="goal-detail"><strong>Action Steps:</strong></div>
          <ul class="action-steps">
            ${goal.action_steps.map((step) => `<li>${step}</li>`).join("")}
          </ul>
        `
            : ""
        }
      </div>
    `
            )
            .join("")
    }
  </div>

  ${
    data.nextSteps.length > 0
      ? `
  <div class="section">
    <div class="section-title">Next Steps</div>
    <ul class="insight-list">
      ${data.nextSteps
        .map(
          (step, index) => `
        <li class="step-item"><strong>${index + 1}.</strong> ${step}</li>
      `
        )
        .join("")}
    </ul>
  </div>
  `
      : ""
  }

  <div class="footer">
    <p>Generated by R2C2 Voice Coach</p>
    <p>Export Date: ${formatDate(new Date())}</p>
  </div>
</body>
</html>
  `;

  return html;
}

/**
 * Export session summary as PDF
 * Opens a print dialog with the formatted content
 */
export function exportAsPDF(data: SessionExportData): void {
  const htmlContent = generateHTMLContent(data);
  
  // Create a new window with the HTML content
  const printWindow = window.open("", "_blank");
  if (!printWindow) {
    alert("Please allow pop-ups to export as PDF");
    return;
  }

  printWindow.document.write(htmlContent);
  printWindow.document.close();

  // Wait for content to load, then trigger print dialog
  printWindow.onload = () => {
    setTimeout(() => {
      printWindow.print();
      // Note: We don't close the window automatically as the user might want to review
      // printWindow.close();
    }, 250);
  };
}

/**
 * Main export function that handles both formats
 */
export function exportSession(
  data: SessionExportData,
  format: "pdf" | "text"
): void {
  if (format === "pdf") {
    exportAsPDF(data);
  } else {
    exportAsText(data);
  }
}
