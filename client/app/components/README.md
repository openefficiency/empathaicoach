# Emotion Visualization Components

This directory contains the emotion visualization components for the R2C2 Voice Coach application.

## Components

### EmotionVisualization.tsx
Displays the current emotional state of the user in real-time.

**Features:**
- Shows emotion icon and label with color coding
- Displays confidence level with progress bar
- Smooth transitions between emotions with animations
- Compact and full display modes
- Subtle, non-distracting design

**Supported Emotions:**
- Neutral (gray)
- Defensive (red)
- Frustrated (orange)
- Sad (blue)
- Anxious (yellow)
- Positive (green)

**Usage:**
```tsx
import { EmotionVisualization } from './components/EmotionVisualization';

<EmotionVisualization
  currentEmotion="positive"
  confidence={0.85}
  showLabel={true}
  compact={false}
/>
```

### EmotionTimeline.tsx
Displays a timeline visualization of emotion changes throughout the session.

**Features:**
- Color-coded timeline showing emotion progression
- Phase transition markers
- Collapsible/expandable view
- Emotion distribution statistics
- Time markers and duration display
- Legend showing all emotions detected

**Usage:**
```tsx
import { EmotionTimeline } from './components/EmotionTimeline';

<EmotionTimeline
  emotions={emotionHistory}
  phaseTransitions={phaseTransitions}
  duration={sessionDuration}
  isCollapsed={true}
/>
```

## Hooks

### useEmotionEvents.ts
Custom React hook for managing emotion events from the backend.

**Features:**
- Listens for emotion detection events via RTVI
- Maintains emotion history throughout the session
- Tracks phase transitions
- Calculates session duration
- Provides emotion trend analysis
- Detects emotion improvement

**Usage:**
```tsx
import { useEmotionEvents } from './hooks/useEmotionEvents';

const {
  currentEmotion,
  currentConfidence,
  emotionHistory,
  phaseTransitions,
  sessionDuration,
  getEmotionTrend,
  isEmotionImproving,
  resetEmotionState,
} = useEmotionEvents();
```

## Integration

The emotion visualization components are integrated into the main ClientApp:

1. **EmotionVisualization** - Displayed in the sidebar showing current emotion
2. **EmotionTimeline** - Displayed below the phase indicator showing emotion history
3. **useEmotionEvents** - Hook used to receive real-time emotion data from the backend

## Backend Integration

The components expect the following RTVI events from the backend:

### Emotion Detection Event
```json
{
  "type": "emotion-detected",
  "data": {
    "emotion": "positive",
    "confidence": 0.85,
    "timestamp": "2025-10-16T12:34:56Z",
    "phase": "reaction"
  }
}
```

### Phase Transition Event
```json
{
  "type": "r2c2-phase-transition",
  "data": {
    "from_phase": "relationship",
    "to_phase": "reaction",
    "timestamp": "2025-10-16T12:34:56Z"
  }
}
```

## Requirements Satisfied

- **Requirement 12.1**: Display current emotion with icon/color
- **Requirement 12.2**: Show confidence level
- **Requirement 12.3**: Build timeline chart showing emotion changes over session
- **Requirement 12.4**: Make visualization subtle and non-distracting
- **Requirement 12.5**: Mark R2C2 phase transitions on timeline
- **Requirement 11.1**: Analyze voice tone for emotional indicators


### ConversationTranscript.tsx
Custom conversation component that displays the transcript of the coaching session.

**Features:**
- Clear distinction between user and coach messages
- Emotion indicators next to user messages (emoji icons with color coding)
- Auto-scrolling to the latest message
- Timestamp for each message
- Styled message bubbles with emotion-based background colors
- Empty state when no messages yet

**Usage:**
```tsx
import { ConversationTranscript } from './components/ConversationTranscript';

<ConversationTranscript
  assistantLabel="Coach"
  clientLabel="You"
  textMode="tts"
/>
```

### FeedbackThemesSidebar.tsx
Sidebar component that displays key feedback themes during the conversation.

**Features:**
- Organized by category (strengths, improvements, neutral)
- Shows frequency of each theme
- Expandable examples from the feedback
- Marks themes as "discussed" when referenced
- Click-to-reference functionality for easy access during conversation
- Color-coded by category with icons
- Responsive design with collapsible sections

**Usage:**
```tsx
import { FeedbackThemesSidebar } from './components/FeedbackThemesSidebar';

<FeedbackThemesSidebar
  themes={feedbackThemes}
  discussedThemes={discussedThemesList}
  onThemeClick={(theme) => console.log('Theme clicked:', theme)}
/>
```

## Requirements Satisfied (Session Transcript)

- **Requirement 7.1**: Transcript displays both user and coach messages
- **Requirement 7.3**: Transcript clearly distinguishes between speakers
- **Requirement 8.8**: Display key feedback themes during conversation with easy reference


### SessionSummary.tsx
Comprehensive session summary component displayed after a coaching session completes.

**Features:**
- Session duration and phase durations breakdown
- Emotional journey summary (start, end, predominant emotions)
- Key insights from the session
- Feedback themes discussed
- Development plan summary with goal breakdown
- Next steps and recommendations
- Export functionality (PDF and text formats)
- Professional, shareable format

**Usage:**
```tsx
import { SessionSummary } from './components/SessionSummary';

<SessionSummary
  sessionId={123}
  userId="user-123"
  startTime={new Date()}
  endTime={new Date()}
  phaseDurations={{
    relationship: 180,
    reaction: 240,
    content: 300,
    coaching: 360
  }}
  emotionalJourney={{
    startEmotion: "anxious",
    endEmotion: "positive",
    predominantEmotion: "neutral",
    emotionChanges: 8
  }}
  keyInsights={["Insight 1", "Insight 2"]}
  feedbackThemesDiscussed={["Theme 1", "Theme 2"]}
  developmentPlan={goals}
  nextSteps={["Step 1", "Step 2"]}
  onExport={(format) => handleExport(format)}
/>
```

## Requirements Satisfied (Session Summary)

- **Requirement 7.2**: Generate structured summary including emotional reactions, feedback themes, and development plan
- **Requirement 7.4**: Display session duration and phase durations
- **Requirement 7.5**: Make summary downloadable/shareable in professional format (PDF or text)
