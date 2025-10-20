# Troubleshooting Guide - R2C2 Voice Coach Frontend

## Common Issues After Refactoring

### Issue: "property 'url': url should be a string" Error

**Symptoms:**
- Error when clicking "Connect" button
- Console shows: `property 'url': url should be a string`
- Connection fails immediately

**Root Cause:**
The frontend is calling the wrong endpoint or the backend is not returning the expected data structure.

**Solution:**

1. **Verify Backend is Running**
   ```bash
   cd r2c2-voice-coach/server
   uv run bot.py --transport daily
   ```
   
   You should see output like:
   ```
   INFO: Started server process
   INFO: Waiting for application startup.
   INFO: Application startup complete.
   ```

2. **Check the Endpoint**
   
   The frontend should call `/start` (Pipecat bot starter), NOT `/api/start`.
   
   In `ClientApp.tsx`, verify:
   ```typescript
   const response = await fetch("/start", {  // ✅ Correct
     method: "POST",
     // ...
   });
   ```
   
   NOT:
   ```typescript
   const response = await fetch("/api/start", {  // ❌ Wrong
     method: "POST",
     // ...
   });
   ```

3. **Test the Endpoint Manually**
   
   ```bash
   curl -X POST http://localhost:7860/start \
     -H "Content-Type: application/json" \
     -d '{"feedback_data": {"themes": []}}'
   ```
   
   Expected response:
   ```json
   {
     "room_url": "https://your-domain.daily.co/room-name",
     "token": "your-token",
     "config": {...}
   }
   ```

4. **Check Environment Variables**
   
   Ensure `server/.env` has:
   ```bash
   DAILY_API_KEY=your_daily_api_key_here
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

### Issue: "Failed to start session: 404"

**Symptoms:**
- 404 error when clicking Connect
- Error shows `POST http://localhost:3000/start 404 (Not Found)`
- Backend logs show no request received

**Root Cause:**
The frontend is calling `/start` on the Next.js dev server (port 3000) instead of the backend bot server (port 7860).

**Solution:**

✅ **Fixed!** A Next.js API route has been created at `app/api/start/route.ts` that proxies requests to the backend.

The proxy route:
1. Receives POST requests at `/api/start`
2. Forwards them to `${NEXT_PUBLIC_API_BASE_URL}/start` (backend)
3. Returns the response to the frontend

**Verify the Fix:**

1. **Check Environment Variable**
   
   In `client/.env.local`:
   ```bash
   NEXT_PUBLIC_API_BASE_URL="http://localhost:7860"
   ```

2. **Restart Next.js Dev Server**
   
   ```bash
   cd client
   npm run dev
   ```

3. **Test the Connection**
   
   - Click "Connect" button
   - Should now successfully connect!

**Alternative: Direct Backend URL**

If the proxy doesn't work, you can temporarily use the full backend URL in `ClientApp.tsx`:

```typescript
const response = await fetch("http://localhost:7860/start", {
  // ...
});
```

But the proxy approach is better for production deployment.

### Issue: No Audio / Microphone Not Working

**Symptoms:**
- Connected successfully but no audio
- Transcript doesn't show user speech
- Microphone button shows as enabled but nothing happens

**Solution:**

1. **Check Browser Permissions**
   - Click the lock icon in browser address bar
   - Ensure microphone is allowed
   - Reload the page

2. **Check Microphone Selection**
   - Open browser settings → Privacy → Microphone
   - Ensure correct microphone is selected
   - Test microphone in system settings

3. **Check Daily.co Connection**
   
   Open browser console and look for:
   ```
   Joined Daily meeting
   Daily call object created with audio subscription enabled
   ```
   
   If you see connection errors, check:
   - Daily.co API key is valid
   - Room URL is accessible
   - Network allows WebRTC connections

4. **Check Audio Subscription**
   
   The `useDailyClient` hook should have:
   ```typescript
   subscribeToTracksAutomatically: true
   ```
   
   This ensures you can hear remote participants (the bot).

### Issue: Can't Hear Bot Speaking

**Symptoms:**
- You can speak and see your transcript
- Backend logs show "Bot started speaking"
- But you don't hear any audio from the bot

**Root Cause:**
Daily.co wasn't configured to subscribe to remote audio tracks.

**Solution:**

✅ **Fixed!** The `useDailyClient` hook now includes `subscribeToTracksAutomatically: true`.

**Verify the Fix:**

1. **Restart Frontend**
   ```bash
   cd client
   npm run dev
   ```

2. **Check Console Logs**
   
   After connecting, you should see:
   ```
   Daily call object created with audio subscription enabled
   Joined Daily meeting
   Track started: {track: {kind: 'audio'}}
   Remote audio track started!
   ```

3. **Test Audio**
   - Speak to the bot
   - Wait for response
   - You should now hear the bot's voice! ✅

**If Still No Audio:**

1. **Check Browser Audio Settings**
   - Ensure browser volume is not muted
   - Check system volume mixer
   - Try a different browser

2. **Check Daily Participants**
   
   In browser console:
   ```javascript
   // Get the Daily call object
   const daily = window.Daily?.instances()[0];
   const participants = daily?.participants();
   console.log(participants);
   ```
   
   You should see the bot participant with audio track.

3. **Test with Daily Prebuilt**
   
   Open the room URL directly in browser:
   ```
   https://aegiswistle.daily.co/aegiswistle
   ```
   
   If you can hear audio there, the issue is in the frontend code.

### Issue: Transcript Not Updating

**Symptoms:**
- Audio works but transcript doesn't show messages
- Bot speaks but text doesn't appear

**Solution:**

1. **Check App Message Handling**
   
   In browser console, add logging:
   ```typescript
   // In useTranscript.ts
   const handleAppMessage = useCallback((event) => {
     console.log("Received app message:", event.data);
     // ...
   });
   ```

2. **Verify Bot is Sending Messages**
   
   Check backend logs for:
   ```
   Sending app message: user-transcription
   Sending app message: bot-tts-text
   ```

3. **Check Event Types**
   
   Ensure backend sends messages with correct types:
   - `user-transcription` for user speech
   - `bot-tts-text` for bot responses
   - `emotion-detected` for emotions

### Issue: "Cannot read property 'join' of null"

**Symptoms:**
- Error when trying to connect
- Daily call object is null

**Solution:**

1. **Check Hook Initialization**
   
   Ensure `useDailyClient` is called at component level:
   ```typescript
   // ✅ Correct - at component level
   function ClientApp() {
     const { connect } = useDailyClient();
     // ...
   }
   ```
   
   NOT inside a callback:
   ```typescript
   // ❌ Wrong - inside callback
   function ClientApp() {
     const handleConnect = () => {
       const { connect } = useDailyClient(); // Error!
     };
   }
   ```

2. **Wait for Initialization**
   
   Add a loading state:
   ```typescript
   const { callObject, connect } = useDailyClient();
   
   if (!callObject) {
     return <div>Initializing...</div>;
   }
   ```

### Issue: TypeScript Errors

**Symptoms:**
- Red squiggly lines in editor
- Build fails with type errors

**Solution:**

1. **Install Type Definitions**
   ```bash
   cd client
   npm install --save-dev @types/node @types/react @types/react-dom
   ```

2. **Check Daily.co Types**
   
   Ensure `@daily-co/daily-js` is installed:
   ```bash
   npm list @daily-co/daily-js
   ```
   
   Should show version `^0.84.0` or higher.

3. **Clear TypeScript Cache**
   ```bash
   rm -rf .next
   rm -rf node_modules/.cache
   npm run dev
   ```

### Issue: "Module not found: Can't resolve '@daily-co/daily-js'"

**Symptoms:**
- Build error about missing Daily.co module
- Import errors in IDE

**Solution:**

1. **Install the Package**
   ```bash
   cd client
   npm install @daily-co/daily-js@^0.84.0
   ```

2. **Verify Installation**
   ```bash
   npm list @daily-co/daily-js
   ```

3. **Restart Dev Server**
   ```bash
   npm run dev
   ```

## Debugging Tips

### Enable Verbose Logging

1. **Frontend (Browser Console)**
   ```typescript
   // In useDailyClient.ts
   useEffect(() => {
     if (callObjectRef.current) {
       callObjectRef.current.on("*", (event) => {
         console.log("Daily event:", event);
       });
     }
   }, []);
   ```

2. **Backend (Server Logs)**
   ```bash
   # In server/.env
   LOG_LEVEL=DEBUG
   ```

### Check Network Traffic

1. Open browser DevTools → Network tab
2. Filter by "WS" (WebSocket) to see Daily.co connections
3. Check for failed requests to `/start`

### Verify Daily.co Room

1. Copy the `room_url` from the response
2. Open it in a new browser tab
3. You should see the Daily.co room interface

## Getting Help

If issues persist:

1. **Check Logs**
   - Browser console (F12)
   - Backend terminal output

2. **Verify Versions**
   ```bash
   # Frontend
   cd client
   npm list @daily-co/daily-js next react
   
   # Backend
   cd server
   uv run python --version
   uv run pip list | grep pipecat
   ```

3. **Test Components Separately**
   - Test backend `/start` endpoint with curl
   - Test Daily.co connection with Daily's test page
   - Test frontend UI without connecting

4. **Create Minimal Reproduction**
   - Isolate the issue to smallest possible code
   - Share error messages and logs
   - Include environment details

