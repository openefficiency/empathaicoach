# Proxy Setup for Backend Communication

## Problem

When the frontend calls `/start`, it was hitting the Next.js dev server (port 3000) instead of the backend bot server (port 7860), resulting in a 404 error.

## Solution

Created a Next.js API route that acts as a proxy to forward requests from the frontend to the backend.

## Architecture

```
Frontend (localhost:3000)
    ↓
    POST /api/start
    ↓
Next.js API Route (app/api/start/route.ts)
    ↓
    Forwards to: ${NEXT_PUBLIC_API_BASE_URL}/start
    ↓
Backend Bot Server (localhost:7860)
    ↓
    Pipecat bot starter creates Daily.co room
    ↓
    Returns { room_url, token }
    ↓
Next.js API Route
    ↓
    Returns response to frontend
    ↓
Frontend connects to Daily.co room
```

## Implementation

### 1. API Route (`app/api/start/route.ts`)

```typescript
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Get backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:7860';
    
    // Forward to backend
    const response = await fetch(`${backendUrl}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Backend error: ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
```

### 2. Frontend Call (`ClientApp.tsx`)

```typescript
const response = await fetch("/api/start", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    feedback_data: sessionState.feedbackData,
  }),
});
```

### 3. Environment Configuration (`.env.local`)

```bash
NEXT_PUBLIC_API_BASE_URL="http://localhost:7860"
```

## Benefits

1. **CORS Handling**: Next.js API routes run on the same origin as the frontend, avoiding CORS issues
2. **Environment Flexibility**: Easy to switch between local/staging/production backends
3. **Error Handling**: Centralized error handling and logging
4. **Security**: Backend URL not exposed in client-side code
5. **Type Safety**: TypeScript support for request/response

## Testing

### 1. Start Backend

```bash
cd r2c2-voice-coach/server
uv run bot.py --transport daily
```

Expected output:
```
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:7860
```

### 2. Start Frontend

```bash
cd r2c2-voice-coach/client
npm run dev
```

Expected output:
```
▲ Next.js 15.5.4
- Local:        http://localhost:3000
```

### 3. Test the Proxy

**Option A: Via Browser**
1. Open http://localhost:3000
2. Upload feedback data
3. Click "Connect"
4. Should connect successfully!

**Option B: Via curl**
```bash
curl -X POST http://localhost:3000/api/start \
  -H "Content-Type: application/json" \
  -d '{"feedback_data": {"themes": []}}'
```

Expected response (Pipecat format):
```json
{
  "dailyRoom": "https://your-domain.daily.co/room-name",
  "dailyToken": "your-token",
  "config": {...}
}
```

The frontend handles both `dailyRoom`/`dailyToken` and `room_url`/`token` formats.

### 4. Verify Backend Received Request

Check backend logs for:
```
INFO: POST /start HTTP/1.1 200 OK
```

## Troubleshooting

### Proxy Returns 500 Error

**Check:**
1. Backend is running on port 7860
2. `NEXT_PUBLIC_API_BASE_URL` is set correctly
3. Backend `/start` endpoint is accessible

**Test backend directly:**
```bash
curl -X POST http://localhost:7860/start \
  -H "Content-Type: application/json" \
  -d '{"feedback_data": {"themes": []}}'
```

### CORS Errors

If you see CORS errors, it means the proxy isn't working and the frontend is trying to call the backend directly.

**Fix:**
1. Ensure you're calling `/api/start` not `/start`
2. Restart Next.js dev server
3. Clear browser cache

### Backend Not Responding

**Check:**
1. Backend is running: `ps aux | grep bot.py`
2. Port 7860 is not blocked by firewall
3. Backend logs for errors

### Environment Variable Not Loading

**Fix:**
1. Restart Next.js dev server after changing `.env.local`
2. Verify variable name starts with `NEXT_PUBLIC_`
3. Check for typos in variable name

## Production Deployment

### Option 1: Same Domain

If frontend and backend are on the same domain:

```bash
# .env.production
NEXT_PUBLIC_API_BASE_URL="https://api.yourcompany.com"
```

The proxy will forward to `https://api.yourcompany.com/start`

### Option 2: Different Domains

If backend is on a different domain, you may need to:

1. **Configure CORS on backend** to allow frontend domain
2. **Use the proxy** to avoid CORS issues
3. **Or call backend directly** if CORS is properly configured

### Option 3: Pipecat Cloud

When deployed to Pipecat Cloud:

```bash
# .env.production
NEXT_PUBLIC_API_BASE_URL="https://api.pipecat.daily.co/v1/public/r2c2-voice-coach"
```

The proxy will forward to the Pipecat Cloud bot starter.

## Alternative: Direct Backend Call

If you prefer to call the backend directly (not recommended for production):

```typescript
// In ClientApp.tsx
const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:7860';
const response = await fetch(`${backendUrl}/start`, {
  method: "POST",
  // ...
});
```

**Pros:**
- Simpler, no proxy needed
- One less network hop

**Cons:**
- CORS issues in production
- Backend URL exposed in client
- Harder to switch environments

## Summary

The proxy setup provides a clean, production-ready way to communicate between the Next.js frontend and the Pipecat backend. It handles CORS, environment switching, and error handling automatically.

**Key Files:**
- `app/api/start/route.ts` - Proxy implementation
- `app/ClientApp.tsx` - Frontend call to `/api/start`
- `.env.local` - Backend URL configuration

**Flow:**
Frontend → `/api/start` → Proxy → Backend `/start` → Daily.co room → Frontend

