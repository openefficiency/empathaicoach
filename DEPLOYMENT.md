# R2C2 Voice Coach - Deployment Guide

This guide provides detailed instructions for deploying the R2C2 Voice Coach to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Local Development Deployment](#local-development-deployment)
- [Pipecat Cloud Deployment](#pipecat-cloud-deployment)
- [Frontend Deployment Options](#frontend-deployment-options)
- [Database Management](#database-management)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Security Best Practices](#security-best-practices)
- [Scaling Considerations](#scaling-considerations)

## Prerequisites

### Required Accounts and Keys

1. **Daily.co Account**
   - Sign up at [https://dashboard.daily.co/](https://dashboard.daily.co/)
   - Create an API key from the Developers section
   - Note: Free tier includes 10,000 minutes/month

2. **Google Gemini API Key**
   - Get your API key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
   - Enable Gemini 2.5 Flash model
   - Note: Check pricing and quotas

3. **Pipecat Cloud Account** (for cloud deployment)
   - Sign up at [https://pipecat.ai/](https://pipecat.ai/)
   - Install CLI: `uv tool install pipecat-cli`
   - Authenticate: `uv run pcc login`

### Required Software

- Python 3.10+ with uv package manager
- Node.js 20+ with npm
- Docker (for Pipecat Cloud deployment)
- Git

## Environment Configuration

### Server Environment Variables

Create `server/.env` with the following configuration:

```bash
# ============================================
# Required Configuration
# ============================================

# Daily.co API Key (Required)
DAILY_API_KEY=your_daily_api_key_here

# Google Gemini API Key (Required)
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Database Path (Required)
DATABASE_PATH=./database/r2c2_sessions.db

# ============================================
# Optional Configuration
# ============================================

# API Server Settings
API_PORT=7860
API_HOST=0.0.0.0
LOG_LEVEL=INFO

# R2C2 Phase Durations (seconds)
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

# Local Development (Optional)
DAILY_SAMPLE_ROOM_URL=https://yourdomain.daily.co/yourroom
DAILY_SAMPLE_ROOM_TOKEN=your_room_token_if_required
```

### Client Environment Variables

Create `client/.env.local`:

```bash
# ============================================
# Bot Connection
# ============================================

# Local Development
BOT_START_URL="http://localhost:7860/start"
BOT_START_PUBLIC_API_KEY=""

# Production (Pipecat Cloud)
# BOT_START_URL="https://api.pipecat.daily.co/v1/public/r2c2-voice-coach/start"
# BOT_START_PUBLIC_API_KEY="pk_your_api_key_here"

# ============================================
# API Configuration
# ============================================

NEXT_PUBLIC_API_BASE_URL="http://localhost:7860"

# ============================================
# Feature Flags
# ============================================

NEXT_PUBLIC_ENABLE_EMOTION_VIZ=true
NEXT_PUBLIC_ENABLE_PLAN_EDITING=true
NEXT_PUBLIC_ENABLE_SESSION_EXPORT=true
NEXT_PUBLIC_DEBUG_MODE=false
NEXT_PUBLIC_AUTO_SCROLL_TRANSCRIPT=true
```

## Local Development Deployment

### Quick Start

1. **Start Backend**:
```bash
cd server
cp env.example .env
# Edit .env with your API keys
uv sync
uv run bot.py --transport daily
```

2. **Start Frontend** (in new terminal):
```bash
cd client
cp env.example .env.local
npm install
npm run dev
```

3. **Access Application**:
   - Open [http://localhost:3000](http://localhost:3000)
   - Click "Start Session"
   - Allow microphone permissions
   - Begin coaching session

### Development with Hot Reload

Both backend and frontend support hot reload:

- **Backend**: Restart `bot.py` after code changes
- **Frontend**: Next.js automatically reloads on file changes

## Pipecat Cloud Deployment

### Step 1: Prepare Configuration

1. **Review deployment settings** in `server/pcc-deploy.toml`:

```toml
agent_name = "r2c2-voice-coach"
image = "r2c2-voice-coach:0.1"
secret_set = "r2c2-voice-coach-secrets"
agent_profile = "agent-2x"
enable_krisp = true

[scaling]
    min_agents = 1
```

2. **Update version** for new deployments:
```toml
image = "r2c2-voice-coach:0.2"  # Increment version
```

### Step 2: Upload Secrets

```bash
cd server

# Upload all secrets from .env file
uv run pcc secrets set r2c2-voice-coach-secrets --file .env

# Verify secrets uploaded
uv run pcc secrets list

# View specific secret (value will be masked)
uv run pcc secrets get r2c2-voice-coach-secrets DAILY_API_KEY
```

### Step 3: Build Docker Image

```bash
# Build and push to Pipecat Cloud registry
uv run pcc docker build-push

# Verify image uploaded
uv run pcc docker images
```

**Troubleshooting Build Issues**:
- Ensure Docker is running
- Check Dockerfile exists in server directory
- Verify sufficient disk space
- Review build logs for errors

### Step 4: Deploy Agent

```bash
# Deploy to Pipecat Cloud
uv run pcc deploy

# Monitor deployment status
uv run pcc status r2c2-voice-coach

# View deployment logs
uv run pcc logs r2c2-voice-coach --follow
```

### Step 5: Get Agent URL

After successful deployment:

```bash
# Get agent details
uv run pcc agent info r2c2-voice-coach
```

Your agent URL will be:
```
https://api.pipecat.daily.co/v1/public/r2c2-voice-coach/start
```

### Step 6: Update Client Configuration

Update `client/.env.local`:

```bash
BOT_START_URL="https://api.pipecat.daily.co/v1/public/r2c2-voice-coach/start"
BOT_START_PUBLIC_API_KEY="pk_your_pipecat_cloud_api_key"
NEXT_PUBLIC_API_BASE_URL="https://api.pipecat.daily.co/v1/public/r2c2-voice-coach"
```

## Frontend Deployment Options

### Option 1: Vercel (Recommended)

Vercel provides seamless Next.js deployment:

```bash
cd client

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow prompts to configure:
# - Project name: r2c2-voice-coach
# - Framework: Next.js
# - Build command: npm run build
# - Output directory: .next

# Set environment variables in Vercel dashboard
# or via CLI:
vercel env add BOT_START_URL
vercel env add BOT_START_PUBLIC_API_KEY
vercel env add NEXT_PUBLIC_API_BASE_URL
```

**Production deployment**:
```bash
vercel --prod
```

### Option 2: Netlify

```bash
cd client

# Build the application
npm run build

# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy

# For production
netlify deploy --prod
```

**Configure environment variables** in Netlify dashboard:
- Site settings → Environment variables
- Add all `NEXT_PUBLIC_*` variables

### Option 3: Docker

Create `client/Dockerfile`:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

Build and run:

```bash
cd client

# Build image
docker build -t r2c2-voice-coach-client .

# Run container
docker run -p 3000:3000 \
  -e BOT_START_URL="https://api.pipecat.daily.co/v1/public/r2c2-voice-coach/start" \
  -e BOT_START_PUBLIC_API_KEY="pk_your_key" \
  -e NEXT_PUBLIC_API_BASE_URL="https://api.pipecat.daily.co/v1/public/r2c2-voice-coach" \
  r2c2-voice-coach-client
```

### Option 4: AWS Amplify

1. Push code to GitHub/GitLab/Bitbucket
2. Connect repository to AWS Amplify
3. Configure build settings:
   - Build command: `npm run build`
   - Output directory: `.next`
4. Add environment variables in Amplify console
5. Deploy

## Database Management

### Local Development

SQLite database is created automatically:

```bash
# Location
server/database/r2c2_sessions.db

# Backup
cp server/database/r2c2_sessions.db server/database/r2c2_sessions.backup.db

# View data
sqlite3 server/database/r2c2_sessions.db
sqlite> .tables
sqlite> SELECT * FROM sessions;
sqlite> .quit
```

### Production Considerations

For production, consider migrating to PostgreSQL:

1. **Why PostgreSQL?**
   - Better concurrency handling
   - Improved performance at scale
   - Better backup and replication options
   - Support for multiple concurrent users

2. **Migration Path**:
   - Export SQLite data: `sqlite3 r2c2_sessions.db .dump > backup.sql`
   - Set up PostgreSQL instance (AWS RDS, Google Cloud SQL, etc.)
   - Update connection string in code
   - Import data to PostgreSQL

3. **Backup Strategy**:
   - Automated daily backups
   - Point-in-time recovery
   - Offsite backup storage
   - Regular backup testing

## Monitoring and Maintenance

### Monitoring Pipecat Cloud Deployment

```bash
# View real-time logs
uv run pcc logs r2c2-voice-coach --follow

# Check agent status
uv run pcc status r2c2-voice-coach

# View metrics
uv run pcc metrics r2c2-voice-coach

# List active sessions
uv run pcc sessions r2c2-voice-coach
```

### Health Checks

Implement health check endpoint in `server/api/routes.py`:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }
```

Test health endpoint:
```bash
curl http://localhost:7860/health
```

### Log Management

**Backend logs**:
- Location: stdout (captured by Pipecat Cloud)
- Level: Set via `LOG_LEVEL` environment variable
- Format: Structured JSON for production

**Frontend logs**:
- Browser console for client-side errors
- Server logs for SSR errors
- Use error tracking service (Sentry, LogRocket)

### Performance Monitoring

Key metrics to monitor:

1. **Response Latency**
   - Target: < 500ms for LLM responses
   - Monitor: Average, p95, p99

2. **Session Duration**
   - Track average session length
   - Monitor completion rates

3. **Error Rates**
   - API errors
   - Connection failures
   - Database errors

4. **Resource Usage**
   - CPU utilization
   - Memory usage
   - Database size

## Security Best Practices

### API Key Management

1. **Never commit secrets to version control**
   - Use `.env` files (gitignored)
   - Use Pipecat Cloud secrets management
   - Rotate keys regularly

2. **Principle of least privilege**
   - Use separate keys for dev/staging/prod
   - Limit API key permissions
   - Monitor key usage

### Data Protection

1. **Encryption**
   - Use HTTPS for all connections
   - Encrypt sensitive data at rest
   - Use secure WebRTC connections

2. **Access Control**
   - Implement user authentication
   - Use session tokens
   - Validate all inputs

3. **Privacy Compliance**
   - GDPR: Right to deletion, data export
   - HIPAA: If handling health data
   - Data retention policies

### Network Security

1. **CORS Configuration**
   - Whitelist allowed origins
   - Restrict API access
   - Use secure headers

2. **Rate Limiting**
   - Prevent abuse
   - Protect API quotas
   - Monitor unusual patterns

## Scaling Considerations

### Horizontal Scaling

Pipecat Cloud handles scaling automatically:

```toml
[scaling]
    min_agents = 1
    max_agents = 10
    scale_up_threshold = 3
    scale_down_delay = 300
```

### Database Scaling

For high traffic:

1. **Read Replicas**
   - Separate read/write operations
   - Use replicas for session history queries

2. **Connection Pooling**
   - Limit concurrent connections
   - Reuse connections efficiently

3. **Caching**
   - Cache frequently accessed data
   - Use Redis for session state

### Cost Optimization

1. **Monitor Usage**
   - Track Daily.co minutes
   - Monitor Gemini API calls
   - Review Pipecat Cloud usage

2. **Optimize Resources**
   - Right-size agent profile
   - Adjust min_agents based on traffic
   - Use auto-scaling effectively

3. **Budget Alerts**
   - Set up billing alerts
   - Monitor quota usage
   - Plan for growth

## Updating Deployments

### Rolling Updates

```bash
cd server

# Update version in pcc-deploy.toml
# image = "r2c2-voice-coach:0.2"

# Build new image
uv run pcc docker build-push

# Deploy update
uv run pcc deploy

# Monitor rollout
uv run pcc logs r2c2-voice-coach --follow
```

### Rollback

If deployment fails:

```bash
# List previous deployments
uv run pcc deployments r2c2-voice-coach

# Rollback to previous version
uv run pcc rollback r2c2-voice-coach <deployment-id>
```

### Zero-Downtime Deployment

Pipecat Cloud provides zero-downtime deployments:
- New agents start before old ones stop
- Traffic gradually shifts to new version
- Automatic health checks

## Support and Resources

- **Pipecat Documentation**: [https://docs.pipecat.ai/](https://docs.pipecat.ai/)
- **Daily.co Documentation**: [https://docs.daily.co/](https://docs.daily.co/)
- **Gemini API Documentation**: [https://ai.google.dev/docs](https://ai.google.dev/docs)
- **Next.js Documentation**: [https://nextjs.org/docs](https://nextjs.org/docs)

For issues specific to R2C2 Voice Coach, refer to the main README troubleshooting section.
