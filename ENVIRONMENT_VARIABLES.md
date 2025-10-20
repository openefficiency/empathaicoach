# R2C2 Voice Coach - Environment Variables Reference

This document provides a comprehensive reference for all environment variables used in the R2C2 Voice Coach application.

## Table of Contents

- [Server Environment Variables](#server-environment-variables)
- [Client Environment Variables](#client-environment-variables)
- [Environment-Specific Configurations](#environment-specific-configurations)
- [Security Considerations](#security-considerations)

## Server Environment Variables

### Required Variables

#### `DAILY_API_KEY`
- **Type**: String
- **Required**: Yes
- **Description**: API key for Daily.co WebRTC service
- **Where to get**: [Daily.co Dashboard](https://dashboard.daily.co/) → Developers → API Keys
- **Example**: `7df8a9b2c3d4e5f6g7h8i9j0k1l2m3n4`
- **Notes**: 
  - Keep this secret and never commit to version control
  - Free tier includes 10,000 minutes/month
  - Used for creating and managing WebRTC rooms

#### `GOOGLE_API_KEY`
- **Type**: String
- **Required**: Yes
- **Description**: API key for Google Gemini AI service
- **Where to get**: [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Example**: `AIzaSyAY3H_bhXWnydY23P_uiSvOcMOzSZ5-GYk`
- **Notes**:
  - Requires Gemini 2.5 Flash model access
  - Monitor usage and quotas
  - Keep secret and rotate regularly

#### `DATABASE_PATH`
- **Type**: String (file path)
- **Required**: Yes
- **Default**: `./database/r2c2_sessions.db`
- **Description**: Path to SQLite database file for session persistence
- **Example**: `./database/r2c2_sessions.db`
- **Notes**:
  - Directory must exist and be writable
  - Relative paths are relative to server directory
  - For production, consider absolute paths
  - Backup regularly

### Optional Variables - API Server

#### `API_PORT`
- **Type**: Integer
- **Required**: No
- **Default**: `7860`
- **Description**: Port number for FastAPI server
- **Example**: `7860`
- **Valid Range**: 1024-65535
- **Notes**:
  - Must not conflict with other services
  - Firewall rules may need adjustment
  - Client must use matching port

#### `API_HOST`
- **Type**: String (IP address)
- **Required**: No
- **Default**: `0.0.0.0`
- **Description**: Host address for FastAPI server to bind to
- **Example**: `0.0.0.0` (all interfaces) or `127.0.0.1` (localhost only)
- **Notes**:
  - `0.0.0.0` allows external connections
  - `127.0.0.1` restricts to localhost only
  - Use `127.0.0.1` for development security

#### `LOG_LEVEL`
- **Type**: String (enum)
- **Required**: No
- **Default**: `INFO`
- **Description**: Logging verbosity level
- **Valid Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**: `INFO`
- **Notes**:
  - `DEBUG`: Detailed information for debugging
  - `INFO`: General informational messages
  - `WARNING`: Warning messages
  - `ERROR`: Error messages
  - `CRITICAL`: Critical errors only
  - Use `DEBUG` for development, `INFO` or `WARNING` for production

### Optional Variables - R2C2 Engine

#### `R2C2_RELATIONSHIP_MIN_DURATION`
- **Type**: Integer (seconds)
- **Required**: No
- **Default**: `120`
- **Description**: Minimum duration for Relationship building phase
- **Example**: `120` (2 minutes)
- **Valid Range**: 60-300
- **Notes**:
  - Phase won't transition before this time
  - Can transition after if conditions met
  - Adjust based on user feedback

#### `R2C2_REACTION_MIN_DURATION`
- **Type**: Integer (seconds)
- **Required**: No
- **Default**: `180`
- **Description**: Minimum duration for Reaction exploration phase
- **Example**: `180` (3 minutes)
- **Valid Range**: 120-600
- **Notes**:
  - Critical phase for processing emotions
  - Longer duration allows deeper exploration
  - Transitions when defensiveness reduces

#### `R2C2_CONTENT_MIN_DURATION`
- **Type**: Integer (seconds)
- **Required**: No
- **Default**: `240`
- **Description**: Minimum duration for Content discussion phase
- **Example**: `240` (4 minutes)
- **Valid Range**: 180-900
- **Notes**:
  - Time needed to review feedback themes
  - Adjust based on feedback complexity
  - Transitions when understanding demonstrated

#### `R2C2_COACHING_MIN_DURATION`
- **Type**: Integer (seconds)
- **Required**: No
- **Default**: `300`
- **Description**: Minimum duration for Coaching for change phase
- **Example**: `300` (5 minutes)
- **Valid Range**: 240-1200
- **Notes**:
  - Time to create development plan
  - Includes goal setting and action planning
  - Session ends when plan is complete

### Optional Variables - Emotion Detection

#### `EMOTION_DETECTION_ENABLED`
- **Type**: Boolean (string)
- **Required**: No
- **Default**: `true`
- **Description**: Enable or disable emotion detection from voice
- **Valid Values**: `true`, `false`
- **Example**: `true`
- **Notes**:
  - Disabling improves performance slightly
  - Emotion data enhances coaching effectiveness
  - Required for emotion visualization in UI

#### `EMOTION_ANALYSIS_WINDOW`
- **Type**: Integer (seconds)
- **Required**: No
- **Default**: `30`
- **Description**: Time window for emotion trend analysis
- **Example**: `30`
- **Valid Range**: 10-120
- **Notes**:
  - Larger window = smoother trends
  - Smaller window = more responsive
  - Used for phase transition decisions

### Optional Variables - Session Management

#### `SESSION_AUTOSAVE_INTERVAL`
- **Type**: Integer (seconds)
- **Required**: No
- **Default**: `120`
- **Description**: Interval for automatic session state saving
- **Example**: `120` (2 minutes)
- **Valid Range**: 30-300
- **Notes**:
  - Prevents data loss on disconnection
  - More frequent = more database writes
  - Balance between safety and performance

#### `MAX_SESSION_DURATION`
- **Type**: Integer (seconds)
- **Required**: No
- **Default**: `3600`
- **Description**: Maximum allowed session duration
- **Example**: `3600` (1 hour)
- **Valid Range**: 1800-7200
- **Notes**:
  - Prevents runaway sessions
  - Session ends gracefully at limit
  - Adjust based on typical session length

### Optional Variables - Local Development

#### `DAILY_SAMPLE_ROOM_URL`
- **Type**: String (URL)
- **Required**: No
- **Default**: None
- **Description**: Pre-created Daily.co room URL for local testing
- **Example**: `https://yourdomain.daily.co/yourroom`
- **Notes**:
  - Optional convenience for development
  - Bot joins this room instead of creating new ones
  - Useful for consistent testing environment

#### `DAILY_SAMPLE_ROOM_TOKEN`
- **Type**: String
- **Required**: No (required if room needs token)
- **Default**: None
- **Description**: Token for accessing the sample room
- **Example**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **Notes**:
  - Only needed if sample room requires authentication
  - Generate from Daily.co dashboard

## Client Environment Variables

### Required Variables

#### `BOT_START_URL`
- **Type**: String (URL)
- **Required**: Yes
- **Description**: Endpoint to start a bot session
- **Local Development**: `http://localhost:7860/start`
- **Production**: `https://api.pipecat.daily.co/v1/public/r2c2-voice-coach/start`
- **Notes**:
  - Must match backend deployment
  - Include `/start` endpoint path
  - Use HTTPS in production

#### `BOT_START_PUBLIC_API_KEY`
- **Type**: String
- **Required**: Yes (for Pipecat Cloud)
- **Default**: Empty string (for local dev)
- **Description**: Pipecat Cloud public API key
- **Example**: `pk_1234567890abcdef`
- **Notes**:
  - Leave empty for local development
  - Required for Pipecat Cloud deployment
  - Public key, safe to expose in client

### Optional Variables - API Configuration

#### `NEXT_PUBLIC_API_BASE_URL`
- **Type**: String (URL)
- **Required**: No
- **Default**: `http://localhost:7860`
- **Description**: Base URL for backend API endpoints
- **Local Development**: `http://localhost:7860`
- **Production**: Your deployed backend URL
- **Notes**:
  - Used for feedback upload, session management
  - Must match backend deployment
  - Include protocol (http/https)

### Optional Variables - Feature Flags

#### `NEXT_PUBLIC_ENABLE_EMOTION_VIZ`
- **Type**: Boolean (string)
- **Required**: No
- **Default**: `true`
- **Description**: Enable emotion visualization in UI
- **Valid Values**: `true`, `false`
- **Example**: `true`
- **Notes**:
  - Requires backend emotion detection enabled
  - Shows real-time emotion indicators
  - Includes emotion timeline

#### `NEXT_PUBLIC_ENABLE_PLAN_EDITING`
- **Type**: Boolean (string)
- **Required**: No
- **Default**: `true`
- **Description**: Allow editing development plan during session
- **Valid Values**: `true`, `false`
- **Example**: `true`
- **Notes**:
  - Users can modify goals in real-time
  - Changes saved to database
  - Disable for view-only mode

#### `NEXT_PUBLIC_ENABLE_SESSION_EXPORT`
- **Type**: Boolean (string)
- **Required**: No
- **Default**: `true`
- **Description**: Enable session export functionality
- **Valid Values**: `true`, `false`
- **Example**: `true`
- **Notes**:
  - Allows PDF/text export of sessions
  - Includes transcript and development plan
  - Useful for sharing with managers

#### `NEXT_PUBLIC_DEBUG_MODE`
- **Type**: Boolean (string)
- **Required**: No
- **Default**: `false`
- **Description**: Enable debug information in UI
- **Valid Values**: `true`, `false`
- **Example**: `false`
- **Notes**:
  - Shows additional logging in console
  - Displays internal state information
  - Use only in development

#### `NEXT_PUBLIC_AUTO_SCROLL_TRANSCRIPT`
- **Type**: Boolean (string)
- **Required**: No
- **Default**: `true`
- **Description**: Automatically scroll transcript to latest message
- **Valid Values**: `true`, `false`
- **Example**: `true`
- **Notes**:
  - Keeps latest message visible
  - User can disable by scrolling up
  - Re-enables when scrolled to bottom

### Optional Variables - Analytics

#### `NEXT_PUBLIC_ANALYTICS_ID`
- **Type**: String
- **Required**: No
- **Default**: Empty string
- **Description**: Analytics tracking ID (Google Analytics, etc.)
- **Example**: `G-XXXXXXXXXX`
- **Notes**:
  - Optional for usage tracking
  - Ensure compliance with privacy policies
  - Anonymize user data

## Environment-Specific Configurations

### Local Development

**Server** (`server/.env`):
```bash
DAILY_API_KEY=your_daily_api_key
GOOGLE_API_KEY=your_google_api_key
DATABASE_PATH=./database/r2c2_sessions.db
API_PORT=7860
API_HOST=127.0.0.1
LOG_LEVEL=DEBUG
EMOTION_DETECTION_ENABLED=true
```

**Client** (`client/.env.local`):
```bash
BOT_START_URL="http://localhost:7860/start"
BOT_START_PUBLIC_API_KEY=""
NEXT_PUBLIC_API_BASE_URL="http://localhost:7860"
NEXT_PUBLIC_DEBUG_MODE=true
```

### Staging Environment

**Server**:
```bash
DAILY_API_KEY=staging_daily_key
GOOGLE_API_KEY=staging_google_key
DATABASE_PATH=/data/r2c2_sessions_staging.db
API_PORT=7860
API_HOST=0.0.0.0
LOG_LEVEL=INFO
SESSION_AUTOSAVE_INTERVAL=60
```

**Client**:
```bash
BOT_START_URL="https://staging-api.yourcompany.com/start"
BOT_START_PUBLIC_API_KEY="pk_staging_key"
NEXT_PUBLIC_API_BASE_URL="https://staging-api.yourcompany.com"
NEXT_PUBLIC_DEBUG_MODE=false
```

### Production Environment

**Server**:
```bash
DAILY_API_KEY=prod_daily_key
GOOGLE_API_KEY=prod_google_key
DATABASE_PATH=/data/r2c2_sessions.db
API_PORT=7860
API_HOST=0.0.0.0
LOG_LEVEL=WARNING
SESSION_AUTOSAVE_INTERVAL=120
MAX_SESSION_DURATION=3600
EMOTION_DETECTION_ENABLED=true
```

**Client**:
```bash
BOT_START_URL="https://api.pipecat.daily.co/v1/public/r2c2-voice-coach/start"
BOT_START_PUBLIC_API_KEY="pk_production_key"
NEXT_PUBLIC_API_BASE_URL="https://api.yourcompany.com"
NEXT_PUBLIC_DEBUG_MODE=false
NEXT_PUBLIC_ANALYTICS_ID="G-XXXXXXXXXX"
```

## Security Considerations

### Secrets Management

1. **Never commit `.env` files to version control**
   - Add to `.gitignore`
   - Use `.env.example` as template

2. **Use different keys for each environment**
   - Separate dev/staging/prod keys
   - Rotate keys regularly
   - Monitor key usage

3. **Pipecat Cloud Secrets**
   - Upload secrets: `uv run pcc secrets set r2c2-voice-coach-secrets --file .env`
   - Secrets are encrypted at rest
   - Access controlled by Pipecat Cloud

### Environment Variable Validation

The application validates required environment variables on startup:

**Server** (`bot.py`):
```python
required_vars = ["DAILY_API_KEY", "GOOGLE_API_KEY", "DATABASE_PATH"]
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    raise ValueError(f"Missing required environment variables: {missing}")
```

**Client** (Next.js):
- Variables prefixed with `NEXT_PUBLIC_` are exposed to browser
- Other variables are server-side only
- Validate in `next.config.ts`

### Best Practices

1. **Use `.env.local` for local overrides** (gitignored by default)
2. **Document all variables** in `.env.example`
3. **Validate on startup** to catch configuration errors early
4. **Use type-safe access** with environment variable libraries
5. **Monitor for exposed secrets** in logs and error messages
6. **Rotate keys regularly** (quarterly recommended)
7. **Use secret management services** for production (AWS Secrets Manager, etc.)

## Troubleshooting

### Variable Not Loading

**Problem**: Environment variable not being read

**Solutions**:
1. Check file name: `.env` (server) or `.env.local` (client)
2. Restart application after changes
3. Verify no typos in variable names
4. Check file is in correct directory
5. For Next.js, ensure `NEXT_PUBLIC_` prefix for client-side variables

### Invalid Value

**Problem**: Application fails with invalid environment variable

**Solutions**:
1. Check value format (string, number, boolean)
2. Verify value is within valid range
3. Check for extra spaces or quotes
4. Validate boolean values are lowercase strings

### Missing Required Variable

**Problem**: Application won't start due to missing variable

**Solutions**:
1. Copy from `.env.example`
2. Check spelling matches exactly
3. Ensure file is named correctly
4. Verify file is in correct directory

## Reference

For more information:
- [Daily.co API Documentation](https://docs.daily.co/)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)
- [Pipecat Cloud Documentation](https://docs.pipecat.ai/)
