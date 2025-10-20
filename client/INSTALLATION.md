# Installation Guide - Refactored Frontend

## Prerequisites

- Node.js 20+ 
- npm or yarn

## Installation Steps

### 1. Install Dependencies

```bash
cd r2c2-voice-coach/client
npm install
```

This will install:
- `@daily-co/daily-js@^0.84.0` - Daily.co WebRTC SDK (newly added)
- All other existing dependencies

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp env.example .env.local
```

Edit `.env.local`:

```bash
# Bot Connection (for local development)
BOT_START_URL="http://localhost:7860/start"
BOT_START_PUBLIC_API_KEY=""

# API Base URL
NEXT_PUBLIC_API_BASE_URL="http://localhost:7860"

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_EMOTION_VIZ=true
NEXT_PUBLIC_ENABLE_PLAN_EDITING=true
NEXT_PUBLIC_ENABLE_SESSION_EXPORT=true
NEXT_PUBLIC_DEBUG_MODE=false
NEXT_PUBLIC_AUTO_SCROLL_TRANSCRIPT=true
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

## Verifying the Installation

1. Open http://localhost:3000
2. You should see the R2C2 Voice Coach welcome screen
3. Upload feedback data
4. Click "Continue to Session"
5. Click "Connect" button
6. If the backend is running, you should connect to a Daily.co room

## Backend Setup

The frontend requires the backend to be running:

```bash
cd r2c2-voice-coach/server
uv run bot.py --transport daily
```

Backend should be running on http://localhost:7860

## Testing the Connection

1. **Check Backend**: Visit http://localhost:7860/health (if health endpoint exists)
2. **Check Frontend**: Open browser console, should see no errors
3. **Test Connection**: 
   - Click "Connect" button
   - Check console for Daily.co connection logs
   - Speak into microphone - transcript should appear

## Troubleshooting

### "Failed to start session" Error

- Ensure backend is running on port 7860
- Check backend logs for errors
- Verify `/api/start` endpoint is accessible

### "Daily connection error"

- Check browser console for detailed error
- Ensure Daily.co API key is configured in backend
- Check network tab for failed requests

### No Audio

- Check microphone permissions in browser
- Ensure microphone is not muted
- Check browser console for audio errors
- Try toggling microphone button

### TypeScript Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Restart dev server
npm run dev
```

## Build for Production

```bash
npm run build
npm start
```

## Key Changes from Previous Version

- **No longer uses Pipecat Client SDK** - Direct Daily.co integration
- **New dependency**: `@daily-co/daily-js@^0.84.0`
- **Custom hooks**: `useDailyClient`, `useTranscript`
- **Custom UI components**: Button, Card, AudioControls

See `REFACTORING_NOTES.md` for detailed changes.

## Support

For issues related to:
- **Daily.co**: Check https://docs.daily.co/
- **Next.js**: Check https://nextjs.org/docs
- **R2C2 Voice Coach**: Check main README.md

