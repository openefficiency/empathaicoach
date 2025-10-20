# 🚀 Simple Cloud Deployment Guide

Since Pipecat Cloud CLI isn't available, here's a simpler approach using alternative platforms.

## Option 1: Deploy to Render.com (Recommended - Easiest)

### Backend Deployment (10 minutes)

1. **Sign up for Render**: https://render.com (free tier available)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `https://github.com/ai-tech-karthik/r2c2-voice-coach`
   - Or use "Deploy from Git URL"

3. **Configure Service**:
   ```
   Name: r2c2-voice-coach-backend
   Region: Choose closest to you
   Branch: main
   Root Directory: server
   Environment: Docker
   ```
   
   **Important**: Select "Docker" as the environment (not Python). The Dockerfile is already configured.

4. **Add Environment Variables** in Render dashboard:
   ```
   DAILY_API_KEY=your_daily_api_key
   GOOGLE_API_KEY=your_gemini_api_key
   DATABASE_PATH=./data/r2c2_coach.db
   PORT=7860
   ```

5. **Deploy**: Click "Create Web Service"
   - First build takes 5-10 minutes
   - Subsequent builds are faster

6. **Get Your Bot URL**: 
   - After deployment, you'll get a URL like: `https://r2c2-voice-coach-backend.onrender.com`
   - Your bot start endpoint: `https://r2c2-voice-coach-backend.onrender.com/start`

**Note**: The Dockerfile has been updated to use a standard Python base image that works across all platforms.

### Frontend Deployment (5 minutes)

1. **Deploy to Vercel**:
   ```bash
   cd client
   npm install -g vercel
   vercel login
   vercel
   ```

2. **Set Environment Variables**:
   ```bash
   vercel env add BOT_START_URL production
   # Enter: https://r2c2-voice-coach-backend.onrender.com/start
   
   vercel env add NEXT_PUBLIC_API_BASE_URL production
   # Enter: https://r2c2-voice-coach-backend.onrender.com
   
   vercel --prod
   ```

---

## Option 2: Deploy to Railway.app (Also Easy)

### Backend Deployment

1. **Sign up for Railway**: https://railway.app (free tier: $5 credit)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure**:
   - Root directory: `server`
   - Start command: `python bot.py --transport daily`

4. **Add Environment Variables** in Railway dashboard:
   ```
   DAILY_API_KEY=your_key
   GOOGLE_API_KEY=your_key
   DATABASE_PATH=./data/r2c2_coach.db
   ```

5. **Deploy**: Railway will auto-deploy

6. **Get URL**: Railway provides a public URL

### Frontend: Same as Option 1 (Vercel)

---

## Option 3: Local Development + Ngrok (Fastest for Demo)

Perfect for hackathon demos when you just need it working quickly!

### Setup (5 minutes)

1. **Install Ngrok**: https://ngrok.com/download

2. **Start Backend Locally**:
   ```bash
   cd server
   cp env.example .env
   # Edit .env with your API keys
   uv sync
   uv run bot.py --transport daily
   ```

3. **Expose Backend with Ngrok** (in new terminal):
   ```bash
   ngrok http 7860
   ```
   
   You'll get a URL like: `https://abc123.ngrok.io`

4. **Update Client Config**:
   ```bash
   cd client
   cp env.example .env.local
   # Edit .env.local:
   BOT_START_URL="https://abc123.ngrok.io/start"
   NEXT_PUBLIC_API_BASE_URL="https://abc123.ngrok.io"
   ```

5. **Start Frontend**:
   ```bash
   npm install
   npm run dev
   ```

6. **Deploy Frontend to Vercel** (optional):
   ```bash
   vercel --prod
   ```

### Pros:
- ✅ Fastest setup (5 minutes)
- ✅ No cloud account needed for backend
- ✅ Perfect for demos
- ✅ Free

### Cons:
- ❌ Ngrok URL changes on restart
- ❌ Not suitable for production
- ❌ Computer must stay on

---

## Option 4: Docker + Any Cloud Provider

### Build Docker Image

```bash
cd server

# Build image
docker build -t r2c2-voice-coach:latest .

# Test locally
docker run -p 7860:7860 \
  -e DAILY_API_KEY=your_key \
  -e GOOGLE_API_KEY=your_key \
  r2c2-voice-coach:latest
```

### Deploy to:

**Google Cloud Run**:
```bash
# Tag for GCR
docker tag r2c2-voice-coach:latest gcr.io/YOUR_PROJECT/r2c2-voice-coach

# Push
docker push gcr.io/YOUR_PROJECT/r2c2-voice-coach

# Deploy
gcloud run deploy r2c2-voice-coach \
  --image gcr.io/YOUR_PROJECT/r2c2-voice-coach \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**AWS ECS/Fargate**: Use AWS Console or CLI

**Azure Container Instances**: Use Azure Portal or CLI

---

## Quick Comparison

| Platform | Setup Time | Cost | Difficulty | Best For |
|----------|------------|------|------------|----------|
| Render.com | 10 min | Free tier | Easy | Hackathons |
| Railway.app | 10 min | $5 credit | Easy | Quick demos |
| Ngrok + Local | 5 min | Free | Easiest | Testing |
| Docker + Cloud | 20 min | Varies | Medium | Production |

---

## Recommended: Render.com + Vercel

This is the easiest cloud deployment:

### Step-by-Step

1. **Backend on Render** (10 minutes):
   - Sign up: https://render.com
   - New Web Service → Connect GitHub
   - Configure as shown above
   - Add environment variables
   - Deploy

2. **Frontend on Vercel** (5 minutes):
   ```bash
   cd client
   vercel login
   vercel
   vercel env add BOT_START_URL production
   vercel --prod
   ```

3. **Test**:
   - Open your Vercel URL
   - Start a session
   - Verify it works!

---

## Troubleshooting

### Backend won't start on Render

**Check logs** in Render dashboard:
- Look for missing dependencies
- Verify environment variables are set
- Check Python version (should be 3.10+)

**Common fixes**:
```bash
# If requirements.txt is missing packages
cd server
pip freeze > requirements.txt
git commit and push
```

### Frontend can't connect to backend

**Verify URLs**:
```bash
# Test backend health
curl https://your-backend.onrender.com/health

# Check CORS settings
# Backend should allow your frontend domain
```

**Update environment variables**:
```bash
vercel env add BOT_START_URL production
# Enter your Render backend URL + /start
vercel --prod
```

### Ngrok URL keeps changing

**Solution**: Get a free Ngrok account for a static domain:
1. Sign up at https://ngrok.com
2. Get your authtoken
3. Run: `ngrok config add-authtoken YOUR_TOKEN`
4. Use: `ngrok http --domain=your-static-domain.ngrok.io 7860`

---

## Cost Estimates

### Free Tier Limits

**Render.com**:
- 750 hours/month free
- Sleeps after 15 min inactivity
- Wakes on request (cold start ~30s)

**Railway.app**:
- $5 free credit
- ~100 hours of usage
- No sleep

**Vercel**:
- Unlimited for hobby projects
- 100GB bandwidth/month

**Ngrok**:
- Free tier: 1 online ngrok process
- 40 connections/minute

### Recommended for Hackathon

**Option 1** (Best): Render + Vercel = $0
**Option 2** (Fastest): Ngrok + Vercel = $0
**Option 3** (Production): Railway + Vercel = $5

---

## Next Steps

1. Choose your deployment option
2. Follow the steps above
3. Test your deployment
4. Record demo video
5. Submit to hackathon!

**Need help?** Check the main TROUBLESHOOTING.md file.
