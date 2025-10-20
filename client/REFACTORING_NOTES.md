# Frontend Refactoring: Pipecat Client to Daily.co Direct Integration

## Overview

This document describes the refactoring of the R2C2 Voice Coach frontend from using the Pipecat Client SDK to using `@daily-co/daily-js` directly.

## Changes Made

### 1. Removed Pipecat Dependencies from ClientApp.tsx

**Before:**
- Used `usePipecatClient` for client management
- Used `usePipecatConnectionState` for connection state
- Used `usePipecatClientCamControl` for camera control
- Used `usePipecatClientScreenShareControl` for screen share control
- Used `PipecatClientVideo` for video display
- Used `PipecatAppBase` wrapper in page.tsx

**After:**
- Created custom `useDailyClient` hook for all Daily.co interactions
- Direct Daily.co WebRTC connection management
- Custom audio/video/screen share controls
- Removed PipecatAppBase wrapper

### 2. New Custom Hooks

#### `useDailyClient` (`app/hooks/useDailyClient.ts`)

A comprehensive hook for managing Daily.co connections:

```typescript
const {
  callObject,           // Direct access to Daily call object
  connectionState,      // 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'
  isConnected,          // Boolean convenience flag
  isConnecting,         // Boolean convenience flag
  isDisconnected,       // Boolean convenience flag
  error,                // Error object if any
  isMicEnabled,         // Microphone state
  isCamEnabled,         // Camera state
  isScreenShareEnabled, // Screen share state
  connect,              // Connect to Daily room
  disconnect,           // Disconnect from Daily room
  toggleMic,            // Toggle microphone
  toggleCam,            // Toggle camera
  startScreenShare,     // Start screen sharing
  stopScreenShare,      // Stop screen sharing
  sendAppMessage,       // Send app messages to bot
} = useDailyClient(config);
```

**Features:**
- Automatic Daily call object initialization
- Event listener management (joined-meeting, left-meeting, error, app-message)
- Audio/video/screen share controls
- App message handling for bot communication

#### `useTranscript` (`app/hooks/useTranscript.ts`)

Manages conversation transcript and emotion tracking:

```typescript
const {
  messages,          // Array of transcript messages
  currentEmotion,    // Current detected emotion
  handleAppMessage,  // Handler for Daily app messages
  clearMessages,     // Clear transcript
} = useTranscript(options);
```

**Features:**
- Processes app messages from Daily.co
- Tracks user and assistant messages
- Tracks emotion detection events
- Avoids duplicate messages

### 3. New UI Components

#### `Button` (`app/components/ui/Button.tsx`)

Custom button component replacing Pipecat's Button:
- Variants: primary, outline, ghost
- Sizes: sm, md, lg
- Full TypeScript support

#### `Card` and `CardContent` (`app/components/ui/Card.tsx`)

Custom card components replacing Pipecat's Card components:
- Consistent styling with dark mode support
- Simple and lightweight

#### `AudioControls` (`app/components/ui/AudioControls.tsx`)

Unified audio/video/screen share controls:
- Microphone toggle with visual feedback
- Camera toggle (optional)
- Screen share toggle (optional)
- Icon-based UI with lucide-react

### 4. Updated Components

#### `ConversationTranscript` (`app/components/ConversationTranscript.tsx`)

**Before:**
- Used `usePipecatEventStream` to get events
- Processed events internally

**After:**
- Receives `messages` array as prop
- Simplified component focused on display
- No event processing logic

#### `ClientApp` (`app/ClientApp.tsx`)

**Major Changes:**
1. Removed all Pipecat imports
2. Uses `useDailyClient` for connection management
3. Uses `useTranscript` for message handling
4. Custom connection flow:
   - Calls `/start` (Pipecat bot starter) to get Daily room URL and token
   - Connects to Daily room directly
   - Handles app messages for bot communication

#### `page.tsx` (`app/page.tsx`)

**Before:**
```tsx
<PipecatAppBase transportType="daily" connectParams={...}>
  {({ handleConnect, handleDisconnect }) => (
    <ClientApp connect={handleConnect} disconnect={handleDisconnect} />
  )}
</PipecatAppBase>
```

**After:**
```tsx
<ClientApp isMobile={isMobile} />
```

All connection logic moved into ClientApp.

## Connection Flow

### Old Flow (Pipecat)
1. PipecatAppBase wraps the app
2. Calls `/api/start` endpoint
3. Pipecat SDK handles Daily.co connection
4. Events flow through Pipecat event system

### New Flow (Direct Daily.co)
1. User clicks "Connect" button
2. ClientApp calls `/api/start` endpoint
3. Receives `{ room_url, token }` from backend
4. `useDailyClient` connects to Daily room directly
5. App messages flow through Daily's `app-message` events
6. `useTranscript` processes messages for display

## Backend Communication

The backend still uses Pipecat for bot logic, but the frontend communicates via:

1. **HTTP API** (`/api/start`): Get Daily room credentials
2. **Daily.co WebRTC**: Audio/video streaming
3. **Daily App Messages**: Bot events (transcription, emotions, phase transitions)

### App Message Format

Messages sent from bot to frontend via Daily app messages:

```typescript
// User transcription
{
  type: "user-transcription",
  data: { text: string }
}

// Bot TTS text
{
  type: "bot-tts-text",
  data: { text: string }
}

// Emotion detection
{
  type: "emotion-detected",
  data: { emotion: EmotionType, confidence: number }
}

// Phase transition
{
  type: "r2c2-phase-transition",
  data: { from_phase: string, to_phase: string }
}
```

## Benefits of This Refactoring

1. **Reduced Dependencies**: No longer dependent on Pipecat client SDK
2. **More Control**: Direct access to Daily.co API
3. **Simpler Architecture**: Clearer separation of concerns
4. **Better Performance**: Fewer abstraction layers
5. **Easier Debugging**: Direct Daily.co event handling
6. **Flexibility**: Can customize Daily.co behavior as needed

## Migration Guide

If you need to add new features:

### Adding New Bot Events

1. Backend emits event via RTVI/Daily app message
2. Add event type to `useTranscript` or create new hook
3. Process event in `handleAppMessage` callback
4. Update UI components to display new data

### Adding New Controls

1. Add method to `useDailyClient` if Daily.co related
2. Create UI component in `app/components/ui/`
3. Wire up in `ClientApp.tsx`

### Customizing Connection

Modify `useDailyClient` hook:
- Add new Daily.co event listeners
- Customize call object configuration
- Add new audio/video settings

## Testing

To test the refactored frontend:

1. Start the backend: `cd server && uv run bot.py --transport daily`
2. Start the frontend: `cd client && npm run dev`
3. Open http://localhost:3000
4. Upload feedback data
5. Click "Connect" - should connect to Daily.co room
6. Speak - audio should work, transcript should appear
7. Test controls - mic, camera, screen share toggles

## Known Issues / TODO

- [ ] Video display component (if needed for camera/screen share)
- [ ] Audio visualizer for microphone input
- [ ] Reconnection logic on network interruption
- [ ] Better error handling and user feedback
- [ ] Loading states during connection

## Dependencies

### Added
- `@daily-co/daily-js@^0.84.0` - **INSTALLED** ✅

### Installation
```bash
cd r2c2-voice-coach/client
npm install
```

### Can Be Removed (Optional Cleanup)
- `@pipecat-ai/client-js` - No longer used in ClientApp
- `@pipecat-ai/client-react` - No longer used in ClientApp
- `@pipecat-ai/voice-ui-kit` - Partially replaced (some components still used)

**Note**: Keep `@pipecat-ai/voice-ui-kit` for now as some components may still be in use (EventStreamPanel, etc.). Can be fully removed after complete audit.

## Files Changed

### New Files
- `app/hooks/useDailyClient.ts`
- `app/hooks/useTranscript.ts`
- `app/components/ui/Button.tsx`
- `app/components/ui/Card.tsx`
- `app/components/ui/AudioControls.tsx`

### Modified Files
- `app/ClientApp.tsx` - Complete rewrite
- `app/page.tsx` - Removed PipecatAppBase
- `app/components/ConversationTranscript.tsx` - Simplified to use props

### Files to Review
- `app/EventStreamPanel.tsx` - May still use Pipecat hooks
- Other components in `app/components/` - Check for Pipecat dependencies

## Conclusion

This refactoring successfully removes the Pipecat client dependency from the frontend while maintaining all functionality. The audio connection now works directly through Daily.co, providing better control and simpler architecture.

