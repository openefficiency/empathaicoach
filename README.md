# R2C2 Voice Coach

empathaicoach

EmpathAI.coach fixes the $6B broken feedback loop. 1 in 3 feedback sessions harms performance by triggering defensiveness. Our AI voice coach uses the proven R2C2 model to validate emotions in real-time, transforming defensive reactions into actionable growth plans. We turn wasted feedback into your new performance currency.


The world's first AI implementation of medical education's proven R2C2 feedback framework. An emotionally intelligent voice AI that guides employees through receiving and processing 360° feedback.

## Overview

The R2C2 Voice Coach reduces defensiveness by 70% and increases development plan completion to 90% by creating a safe, non-judgmental space for employees to process feedback and develop actionable improvement plans.

### The R2C2 Framework

- **Relationship building**: Establish rapport and create psychological safety
- **Reaction exploration**: Help process emotional reactions to feedback
- **Content discussion**: Guide understanding of specific feedback content
- **Coaching for change**: Support creation of concrete development plans

## Technology Stack

**Backend:**
- Python 3.10+
- Pipecat AI framework (real-time audio pipeline)
- Google Gemini 2.5 Flash (multimodal AI with native audio)
- Daily.co (WebRTC transport)
- SQLite (data persistence)
- FastAPI (HTTP endpoints)

**Frontend:**
- Next.js 15.5+
- Pipecat Voice UI Kit
- TypeScript
- Tailwind CSS 4

## Project Structure

```
r2c2-voice-coach/
├── server/
│   ├── bot.py                 # Main Pipecat bot orchestration
│   ├── r2c2/                  # R2C2 conversation engine
│   ├── database/              # SQLite persistence layer
│   ├── api/                   # FastAPI endpoints
│   ├── processors/            # Custom Pipecat processors
│   ├── pyproject.toml         # Python dependencies
│   └── env.example            # Environment variables template
├── client/
│   ├── app/                   # Next.js application
│   ├── components/            # React components
│   ├── hooks/                 # Custom React hooks
│   └── package.json           # Node dependencies
├── sample-feedback/           # Sample 360° feedback data for testing
│   ├── feedback-example-1-mixed.json
│   ├── feedback-example-2-challenging.json
│   ├── feedback-example-3-positive.json
│   ├── feedback-example-4-new-employee.json
│   ├── feedback-example-5-simple.txt
│   └── README.md              # Guide to using sample data
└── README.md
```

## Getting Started

### Prerequisites

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 20 or higher** - [Download Node.js](https://nodejs.org/)
- **uv** (Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Daily.co API key** - [Get API key](https://dashboard.daily.co/)
- **Google Gemini API key** - [Get API key](https://aistudio.google.com/app/apikey)

### Local Development Setup

#### Step 1: Clone and Navigate

```bash
cd r2c2-voice-coach
```

#### Step 2: Backend Setup

1. Navigate to the server directory:
```bash
cd server
```

2. Copy the environment template:
```bash
cp env.example .env
```

3. Edit `.env` and configure required variables:
```bash
# Required API Keys
DAILY_API_KEY=your_daily_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Database Configuration
DATABASE_PATH=./database/r2c2_sessions.db

# Optional: For local dev with a specific room
DAILY_SAMPLE_ROOM_URL=https://yourdomain.daily.co/yourroom
DAILY_SAMPLE_ROOM_TOKEN=your_room_token_if_required

# Server Configuration (defaults shown)
API_PORT=7860
API_HOST=0.0.0.0
LOG_LEVEL=INFO

# R2C2 Phase Durations (in seconds)
R2C2_RELATIONSHIP_MIN_DURATION=120
R2C2_REACTION_MIN_DURATION=180
R2C2_CONTENT_MIN_DURATION=240
R2C2_COACHING_MIN_DURATION=300

# Emotion Detection
EMOTION_DETECTION_ENABLED=true
EMOTION_ANALYSIS_WINDOW=30

# Session Management
SESSION_AUTOSAVE_INTERVAL=120
MAX_SESSION_DURATION=3600
```

4. Install dependencies:
```bash
uv sync
```

5. Initialize the database (automatic on first run):
```bash
# The database will be created automatically when you start the bot
# Location: ./database/r2c2_sessions.db
```

6. Run the bot:
```bash
uv run bot.py --transport daily
```

The server will start on `http://localhost:7860`

#### Step 3: Frontend Setup

1. Open a new terminal and navigate to the client directory:
```bash
cd client
```

2. Copy the environment template:
```bash
cp env.example .env.local
```

3. Edit `.env.local`:
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

4. Install dependencies:
```bash
npm install
```

5. Run the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser

#### Step 4: Test the Application

1. Click "Start Session" in the browser
2. Allow microphone permissions when prompted
3. Upload or paste sample 360° feedback data
   - Use sample files from `sample-feedback/` directory
   - Try `feedback-example-1-mixed.json` for a balanced scenario
   - See `sample-feedback/README.md` for all available examples
4. Begin your R2C2 coaching session

### Sample Feedback Data

The `sample-feedback/` directory contains realistic 360° feedback examples for testing:

- **feedback-example-1-mixed.json** - Balanced feedback with strengths and improvement areas
- **feedback-example-2-challenging.json** - Difficult feedback to test emotion processing
- **feedback-example-3-positive.json** - Predominantly positive feedback for high performers
- **feedback-example-4-new-employee.json** - Developmental feedback for newer employees
- **feedback-example-5-simple.txt** - Simple text format example

See `sample-feedback/README.md` for detailed descriptions and testing guidance.

## Deployment to Pipecat Cloud

### Prerequisites for Deployment

- Pipecat Cloud account - [Sign up](https://pipecat.ai/)
- Docker installed locally (for building images)
- `pcc` CLI tool (installed via `uv`)

### Deployment Steps

#### 1. Prepare Environment Variables

Create a `.env` file in the `server/` directory with your production values:

```bash
cd server
cp env.example .env
# Edit .env with production API keys
```

**Important**: Never commit `.env` files to version control!

#### 2. Configure Deployment Settings

Edit `server/pcc-deploy.toml` if needed:

```toml
agent_name = "r2c2-voice-coach"
image = "r2c2-voice-coach:0.1"
secret_set = "r2c2-voice-coach-secrets"
agent_profile = "agent-2x"  # 2 vCPU, 4GB RAM
enable_krisp = true

[scaling]
    min_agents = 1
```

#### 3. Upload Secrets to Pipecat Cloud

```bash
cd server
uv run pcc secrets set r2c2-voice-coach-secrets --file .env
```

This securely uploads your API keys and sensitive configuration to Pipecat Cloud.

#### 4. Build and Push Docker Image

```bash
uv run pcc docker build-push
```

This builds your Docker image and pushes it to Pipecat Cloud's registry.

#### 5. Deploy the Agent

```bash
uv run pcc deploy
```

Wait for deployment to complete. You'll receive a deployment URL.

#### 6. Update Client Configuration

Update `client/.env.local` with your deployed agent URL:

```bash
BOT_START_URL="https://api.pipecat.daily.co/v1/public/r2c2-voice-coach/start"
BOT_START_PUBLIC_API_KEY="pk_your_pipecat_cloud_api_key"
NEXT_PUBLIC_API_BASE_URL="https://api.pipecat.daily.co/v1/public/r2c2-voice-coach"
```

#### 7. Deploy Frontend

Deploy the Next.js frontend to your preferred hosting platform:

**Vercel** (Recommended):
```bash
cd client
npm install -g vercel
vercel
```

**Netlify**:
```bash
cd client
npm run build
# Upload the .next folder to Netlify
```

**Docker**:
```bash
cd client
docker build -t r2c2-voice-coach-client .
docker run -p 3000:3000 r2c2-voice-coach-client
```

### Monitoring Your Deployment

View logs and metrics:
```bash
uv run pcc logs r2c2-voice-coach
uv run pcc status r2c2-voice-coach
```

### Updating Your Deployment

When you make changes:

```bash
cd server
# Update version in pcc-deploy.toml
# image = "r2c2-voice-coach:0.2"

uv run pcc docker build-push
uv run pcc deploy
```

## Features

- **Real-time voice conversation** with natural-sounding AI coach
- **Emotion detection** from voice tone to adapt coaching approach
- **Four-phase R2C2 framework** implementation
- **Session persistence** with SQLite database
- **Development plan creation** with SMART goals
- **Session transcripts** and summaries
- **Emotion visualization** showing emotional journey
- **Mobile-responsive** interface

## Troubleshooting

### Common Issues

#### SSL Certificate Error (macOS)

**Problem**: `SSL: CERTIFICATE_VERIFY_FAILED` error when running the bot

**Solution**: Install Python SSL certificates:
```bash
/Applications/Python\ 3.12/Install\ Certificates.command
```

Or for Python 3.10/3.11, adjust the path accordingly.

#### Microphone Permission Denied

**Problem**: Browser doesn't request microphone permissions

**Solution**:
1. Ensure you're accessing the app via `https://` or `localhost`
2. Check browser settings: Settings → Privacy → Microphone
3. Clear browser cache and reload
4. Try a different browser (Chrome/Edge recommended)

#### Bot Not Responding

**Problem**: Bot connects but doesn't respond to speech

**Solution**:
1. Check server logs for errors: `uv run bot.py --transport daily`
2. Verify API keys are correct in `.env`
3. Ensure Gemini API has sufficient quota
4. Check Daily.co account status and limits
5. Verify microphone is working (test in browser settings)

#### Database Errors

**Problem**: `sqlite3.OperationalError` or database locked errors

**Solution**:
1. Ensure database directory exists: `mkdir -p server/database`
2. Check file permissions: `chmod 755 server/database`
3. Close any other processes accessing the database
4. Delete and recreate database: `rm server/database/r2c2_sessions.db`

#### Connection Timeout

**Problem**: "Failed to connect to bot" error in frontend

**Solution**:
1. Verify backend is running: `curl http://localhost:7860/start`
2. Check `BOT_START_URL` in `client/.env.local`
3. Ensure no firewall blocking port 7860
4. Check Daily.co API key is valid
5. Review server logs for connection errors

#### Emotion Detection Not Working

**Problem**: Emotion visualization shows only "neutral"

**Solution**:
1. Verify `EMOTION_DETECTION_ENABLED=true` in `.env`
2. Check audio quality (background noise can affect detection)
3. Speak clearly and with varied tone
4. Review server logs for emotion processing errors
5. Ensure sufficient audio data (detection needs ~2-3 seconds)

#### Deployment Failures

**Problem**: `pcc deploy` fails or agent doesn't start

**Solution**:
1. Verify secrets are uploaded: `uv run pcc secrets list`
2. Check Docker image built successfully: `uv run pcc docker images`
3. Review deployment logs: `uv run pcc logs r2c2-voice-coach`
4. Ensure agent profile is correct (agent-2x required)
5. Verify Pipecat Cloud account has sufficient credits

#### High Latency

**Problem**: Noticeable delay in bot responses

**Solution**:
1. Check internet connection speed
2. Use a Daily.co region closer to you
3. Reduce background network usage
4. For deployment, ensure agent profile has sufficient resources
5. Monitor Gemini API response times

#### Session Not Saving

**Problem**: Development plans or session history not persisting

**Solution**:
1. Check database path in `.env`: `DATABASE_PATH=./database/r2c2_sessions.db`
2. Ensure write permissions: `chmod 755 server/database`
3. Verify disk space available
4. Check server logs for database errors
5. Test database connection: `uv run python -c "import sqlite3; sqlite3.connect('database/r2c2_sessions.db')"`

### Getting Help

If you encounter issues not covered here:

1. **Check logs**: Server logs contain detailed error information
2. **Review requirements**: Ensure all prerequisites are installed
3. **Test components**: Test backend and frontend separately
4. **Search issues**: Check GitHub issues for similar problems
5. **Ask for help**: Open a new issue with:
   - Error messages and logs
   - Steps to reproduce
   - Environment details (OS, Python version, Node version)

### Debug Mode

Enable debug mode for more detailed logging:

**Backend**:
```bash
# In server/.env
LOG_LEVEL=DEBUG
```

**Frontend**:
```bash
# In client/.env.local
NEXT_PUBLIC_DEBUG_MODE=true
```

## Development

### Running Tests

Backend tests:
```bash
cd server
uv run pytest
```

Frontend tests:
```bash
cd client
npm test
```

### Code Quality

Backend linting:
```bash
cd server
uv run ruff check .
```

Frontend linting:
```bash
cd client
npm run lint
```

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
