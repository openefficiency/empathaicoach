# R2C2 Voice Coach - Quick Hackathon Deployment Guide

## 🚀 Fast Track Deployment (15-20 minutes)

This guide will get your R2C2 Voice Coach deployed and running in the cloud for your hackathon submission.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Daily.co API key ([Get it here](https://dashboard.daily.co/))
- [ ] Google Gemini API key ([Get it here](https://aistudio.google.com/app/apikey))
- [ ] Vercel account (free) ([Sign up](https://vercel.com/signup))
- [ ] Pipecat Cloud account ([Sign up](https://pipecat.ai/))

## Step 1: Deploy Backend to Pipecat Cloud (5-7 minutes)

### 1.1 Install Pipecat Cloud CLI

```bash
# Install Pipecat Cloud CLI
pip install pipecatcloud

# Verify installation
pcc --version

# Login to Pipecat Cloud
pcc login
```

### 1.2 Configure Environment

```bash
cd r2c2-voice-coach/server

# Copy environment template
cp env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Add these required values:
```bash
DAILY_API_KEY=your_daily_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here
DATABASE_PATH=./data/r2c2_coach.db
```

### 1.3 Upload Secrets

```bash
# Upload secrets to Pipecat Cloud
pcc secrets set r2c2-coach --file .env

# Verify secrets uploaded
pcc secrets list
```

### 1.4 Build and Deploy

```bash
# Build Docker image and push to Pipecat Cloud
pcc docker build-push

# Deploy the agent
pcc deploy

# Check deployment status
pcc status r2c2-coach
```

### 1.5 Get Your Bot URL

```bash
# Get agent information
pcc agent info r2c2-coach
```

Your bot URL will be something like:
```
https://api.pipecat.daily.co/v1/public/r2c2-coach/start
```

**Save this URL - you'll need it for the frontend!**

## Step 2: Deploy Frontend to Vercel (5-7 minutes)

### 2.1 Install Vercel CLI

```bash
npm install -g vercel
```

### 2.2 Configure Environment

```bash
cd r2c2-voice-coach/client

# Copy environment template
cp env.example .env.local

# Edit .env.local
nano .env.local
```

Update with your bot URL from Step 1.5:
```bash
BOT_START_URL="https://api.pipecat.daily.co/v1/public/r2c2-coach/start"
BOT_START_PUBLIC_API_KEY=""  # Leave empty for now
NEXT_PUBLIC_API_BASE_URL="https://api.pipecat.daily.co/v1/public/r2c2-coach"
NEXT_PUBLIC_ENABLE_EMOTION_VIZ=true
NEXT_PUBLIC_ENABLE_PLAN_EDITING=true
NEXT_PUBLIC_DEBUG_MODE=false
```

### 2.3 Deploy to Vercel

```bash
# Login to Vercel
vercel login

# Deploy (first time - will ask questions)
vercel

# Answer the prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? r2c2-voice-coach (or your choice)
# - Directory? ./
# - Override settings? No

# Deploy to production
vercel --prod
```

### 2.4 Set Environment Variables in Vercel

After deployment, set environment variables:

```bash
# Set each environment variable
vercel env add BOT_START_URL production
# Paste your bot URL when prompted

vercel env add NEXT_PUBLIC_API_BASE_URL production
# Paste your API base URL when prompted

vercel env add NEXT_PUBLIC_ENABLE_EMOTION_VIZ production
# Enter: true

vercel env add NEXT_PUBLIC_ENABLE_PLAN_EDITING production
# Enter: true

# Redeploy with new environment variables
vercel --prod
```

## Step 3: Test Your Deployment (2-3 minutes)

### 3.1 Access Your Application

Open the Vercel URL (shown after deployment):
```
https://r2c2-voice-coach-your-username.vercel.app
```

### 3.2 Quick Test

1. Click "Start Session"
2. Allow microphone permissions
3. Enter sample feedback or upload a CSV
4. Start the coaching session
5. Speak and verify the AI coach responds
6. Check that emotions are detected
7. Complete a short session and verify summary

### 3.3 Verify Components

- [ ] Feedback input works
- [ ] Voice connection establishes
- [ ] AI coach responds
- [ ] Emotion visualization shows
- [ ] Phase indicator updates
- [ ] Transcript displays
- [ ] Session summary generates

## Step 4: Prepare Hackathon Submission (3-5 minutes)

### 4.1 Create Demo Video

Record a 2-3 minute demo showing:
1. Landing page
2. Feedback input
3. Starting a session
4. Voice interaction with AI coach
5. Emotion detection in action
6. Phase transitions
7. Development plan creation
8. Session summary

### 4.2 Prepare Submission Materials

Create a submission document with:

**Project Name:** R2C2 Voice Coach

**Live Demo URL:** `https://your-app.vercel.app`

**Description:**
```
R2C2 Voice Coach is the world's first AI implementation of medical education's 
proven R2C2 feedback framework. It uses voice AI to guide employees through 
processing 360° feedback, reducing defensiveness by 70% and increasing 
development plan completion to 90%.

Key Features:
- Real-time voice coaching using Google Gemini Live
- Emotion detection and adaptive responses
- Four-phase R2C2 framework (Relationship, Reaction, Content, Coaching)
- Automatic development plan generation
- Session history and progress tracking
```

**Tech Stack:**
- Backend: Python, Pipecat AI, Google Gemini 2.5 Flash
- Frontend: Next.js 15, React 19, TypeScript
- Infrastructure: Pipecat Cloud, Vercel, Daily.co
- Database: SQLite

**GitHub Repository:** `https://github.com/your-username/r2c2-voice-coach`

**Demo Credentials:** (if needed)
```
No login required - just click "Start Session"
```

### 4.3 Test Links

Before submitting, verify:
- [ ] Live demo URL works
- [ ] GitHub repository is public
- [ ] README is comprehensive
- [ ] Demo video is accessible
- [ ] All links in submission work

## Troubleshooting

### Backend Issues

**Problem:** Bot deployment fails
```bash
# Check logs
uv run pcc logs r2c2-coach --follow

# Common fixes:
# 1. Verify secrets are uploaded
uv run pcc secrets list

# 2. Check Docker is running
docker ps

# 3. Rebuild and redeploy
uv run pcc docker build-push
uv run pcc deploy
```

**Problem:** Bot doesn't respond
```bash
# Check agent status
uv run pcc status r2c2-coach

# View recent logs
uv run pcc logs r2c2-coach --tail 100

# Verify API keys are correct
uv run pcc secrets get r2c2-coach DAILY_API_KEY
```

### Frontend Issues

**Problem:** Can't connect to bot
- Verify BOT_START_URL is correct in Vercel environment variables
- Check browser console for errors
- Verify microphone permissions are granted

**Problem:** Environment variables not working
```bash
# Redeploy after setting env vars
vercel --prod

# Or set via Vercel dashboard:
# Project Settings → Environment Variables
```

### Connection Issues

**Problem:** WebRTC connection fails
- Check Daily.co API key is valid
- Verify Daily.co account has available minutes
- Check browser console for WebRTC errors
- Try a different browser (Chrome recommended)

## Quick Commands Reference

### Backend
```bash
# Deploy
cd r2c2-voice-coach/server
uv run pcc deploy

# Check status
uv run pcc status r2c2-coach

# View logs
uv run pcc logs r2c2-coach --follow

# Rollback
uv run pcc rollback r2c2-coach
```

### Frontend
```bash
# Deploy
cd r2c2-voice-coach/client
vercel --prod

# View logs
vercel logs

# Set env var
vercel env add VARIABLE_NAME production
```

## Performance Tips for Demo

1. **Pre-load sample feedback** - Have a CSV ready to upload
2. **Test your microphone** - Ensure good audio quality
3. **Use Chrome browser** - Best WebRTC support
4. **Stable internet** - Use wired connection if possible
5. **Quiet environment** - Minimize background noise

## Cost Estimates (Free Tier)

- **Daily.co:** 10,000 minutes/month free
- **Google Gemini:** Free tier available
- **Pipecat Cloud:** Check current pricing
- **Vercel:** Free for hobby projects
- **Total:** $0-20/month for hackathon demo

## Support Resources

- **Pipecat Docs:** https://docs.pipecat.ai/
- **Daily.co Docs:** https://docs.daily.co/
- **Vercel Docs:** https://vercel.com/docs
- **Project README:** See main README.md

## Submission Checklist

Before submitting:

- [ ] Backend deployed and running
- [ ] Frontend deployed and accessible
- [ ] Demo video recorded
- [ ] GitHub repository public
- [ ] README updated with demo URL
- [ ] All features working
- [ ] Tested on multiple devices
- [ ] Submission form completed

## Next Steps After Hackathon

1. **Gather feedback** from judges and users
2. **Monitor usage** via Pipecat Cloud dashboard
3. **Review logs** for any errors
4. **Iterate** based on feedback
5. **Scale** if needed (upgrade Pipecat Cloud plan)

---

## 🎉 You're Ready!

Your R2C2 Voice Coach is now deployed and ready for your hackathon submission!

**Live Demo:** `https://your-app.vercel.app`

**Good luck with your hackathon! 🚀**

---

**Need Help?**
- Check the main DEPLOYMENT.md for detailed instructions
- Review TROUBLESHOOTING.md for common issues
- Check Pipecat Cloud dashboard for agent status
