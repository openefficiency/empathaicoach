# 🚀 Pipecat Cloud - Quick Start Guide

## Official Pipecat Cloud Deployment

Deploy your R2C2 Voice Coach to Pipecat Cloud in 15 minutes!

**Official Site:** https://www.daily.co/products/pipecat-cloud/

---

## Prerequisites

1. **Sign up for Pipecat Cloud**: https://pipecat.daily.co/sign-up
2. **Get API Keys**:
   - Daily.co: https://dashboard.daily.co/
   - Google Gemini: https://aistudio.google.com/app/apikey

---

## Step 1: Install Pipecat Cloud CLI (2 minutes)

```bash
# Install the CLI
pip install pipecatcloud

# Verify installation
pcc --version

# Login to Pipecat Cloud
pcc login
```

This will open your browser for authentication.

---

## Step 2: Configure Your Project (2 minutes)

```bash
cd r2c2-voice-coach/server

# Create .env file with your API keys
cp env.example .env

# Edit .env and add:
# DAILY_API_KEY=your_daily_api_key
# GOOGLE_API_KEY=your_gemini_api_key
# DATABASE_PATH=./data/r2c2_coach.db
```

---

## Step 3: Upload Secrets (1 minute)

```bash
# Upload all secrets from .env file
pcc secrets set r2c2-coach --file .env

# Verify secrets were uploaded
pcc secrets list

# View a specific secret (value will be masked)
pcc secrets get r2c2-coach DAILY_API_KEY
```

---

## Step 4: Build & Deploy (5-10 minutes)

```bash
# Build Docker image and push to Pipecat Cloud
pcc docker build-push

# Deploy your agent
pcc deploy

# Check deployment status
pcc status r2c2-coach
```

**Note:** First build may take 5-10 minutes. Subsequent builds are faster.

---

## Step 5: Get Your Bot URL (1 minute)

```bash
# Get agent information
pcc agent info r2c2-coach
```

Your bot URL will be:
```
https://api.pipecat.daily.co/v1/public/r2c2-coach/start
```

**Save this URL!** You'll need it for the frontend.

---

## Step 6: Deploy Frontend to Vercel (5 minutes)

```bash
cd ../client

# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Create .env.local with your bot URL
cat > .env.local << EOF
BOT_START_URL="https://api.pipecat.daily.co/v1/public/r2c2-coach/start"
BOT_START_PUBLIC_API_KEY=""
NEXT_PUBLIC_API_BASE_URL="https://api.pipecat.daily.co/v1/public/r2c2-coach"
NEXT_PUBLIC_ENABLE_EMOTION_VIZ=true
NEXT_PUBLIC_ENABLE_PLAN_EDITING=true
NEXT_PUBLIC_DEBUG_MODE=false
EOF

# Install dependencies
npm install

# Deploy to Vercel
vercel --prod
```

---

## Step 7: Test Your Deployment (2 minutes)

1. Open your Vercel URL
2. Click "Start Session"
3. Allow microphone permissions
4. Enter sample feedback
5. Start coaching and verify it works!

---

## Useful Commands

### Monitoring

```bash
# View real-time logs
pcc logs r2c2-coach --follow

# View last 100 lines
pcc logs r2c2-coach --tail 100

# Check agent status
pcc status r2c2-coach

# View agent metrics
pcc metrics r2c2-coach

# List active sessions
pcc sessions r2c2-coach
```

### Updating

```bash
# Update code and redeploy
pcc docker build-push
pcc deploy

# Update secrets
pcc secrets set r2c2-coach VARIABLE_NAME=new_value

# Or update from file
pcc secrets set r2c2-coach --file .env
```

### Troubleshooting

```bash
# View deployment history
pcc deployments r2c2-coach

# Rollback to previous version
pcc rollback r2c2-coach <deployment-id>

# Delete agent (careful!)
pcc delete r2c2-coach
```

---

## Configuration File

Your deployment is configured in `server/pcc-deploy.toml`:

```toml
agent_name = "r2c2-coach"
image = "r2c2-voice-coach:0.1"
secret_set = "r2c2-coach-secrets"
agent_profile = "agent-2x"
enable_krisp = true

[scaling]
    min_agents = 1
```

**Agent Profiles:**
- `agent-1x`: 1 vCPU, 2GB RAM (basic)
- `agent-2x`: 2 vCPU, 4GB RAM (recommended)
- `agent-4x`: 4 vCPU, 8GB RAM (high performance)

---

## Troubleshooting

### Issue: "pcc: command not found"

**Solution:**
```bash
# Reinstall pipecatcloud
pip install --upgrade pipecatcloud

# Or use python -m
python -m pipecatcloud --version
```

### Issue: "Not authenticated"

**Solution:**
```bash
# Login again
pcc login

# Verify
pcc whoami
```

### Issue: "Docker build failed"

**Solution:**
```bash
# Make sure Docker is running
docker ps

# Check Dockerfile exists
ls server/Dockerfile

# Try building locally first
cd server
docker build -t r2c2-test .
```

### Issue: "Secrets not found"

**Solution:**
```bash
# List all secrets
pcc secrets list

# Re-upload secrets
cd server
pcc secrets set r2c2-coach --file .env

# Verify
pcc secrets get r2c2-coach DAILY_API_KEY
```

### Issue: "Agent not responding"

**Solution:**
```bash
# Check agent status
pcc status r2c2-coach

# View logs
pcc logs r2c2-coach --tail 100

# Verify secrets are correct
pcc secrets list

# Redeploy
pcc deploy
```

---

## Cost & Limits

### Pipecat Cloud Pricing

Check current pricing at: https://pipecat.daily.co/pricing

**Free Tier** (if available):
- Limited agent hours
- Basic support
- Community access

**Paid Plans:**
- Pay-as-you-go or monthly
- Higher limits
- Priority support
- Enterprise features

### Daily.co Limits

**Free Tier:**
- 10,000 minutes/month
- Unlimited rooms
- Basic features

### Google Gemini Limits

**Free Tier:**
- 15 requests/minute
- 1,500 requests/day
- Check: https://ai.google.dev/pricing

---

## Production Checklist

Before going to production:

- [ ] Secrets uploaded and verified
- [ ] Agent deployed and running
- [ ] Frontend deployed to Vercel
- [ ] All features tested
- [ ] Monitoring set up
- [ ] Error tracking configured
- [ ] Backup strategy in place
- [ ] Scaling limits configured
- [ ] Budget alerts set up
- [ ] Documentation updated

---

## Support

### Official Resources

- **Pipecat Cloud Docs**: https://docs.pipecat.daily.co/
- **Pipecat GitHub**: https://github.com/pipecat-ai/pipecat
- **Daily.co Discord**: https://discord.gg/dailyco
- **Support**: support@daily.co

### Project Resources

- **Deployment Guide**: See DEPLOYMENT.md
- **Troubleshooting**: See TROUBLESHOOTING.md
- **Quick Start**: See QUICK_START.md

---

## Quick Deployment Script

Use the automated script:

```bash
cd r2c2-voice-coach

# Make sure you have .env configured
cp server/env.example server/.env
# Edit server/.env with your API keys

# Run deployment script
./deploy-hackathon.sh
```

The script will:
1. Install Pipecat Cloud CLI
2. Upload secrets
3. Build and deploy backend
4. Deploy frontend to Vercel
5. Give you your live URLs

---

## Next Steps

1. **Test thoroughly** - Try all features
2. **Monitor logs** - Watch for errors
3. **Optimize** - Adjust agent profile if needed
4. **Scale** - Configure auto-scaling
5. **Iterate** - Deploy updates as needed

---

**You're ready to deploy! 🚀**

Run: `./deploy-hackathon.sh` or follow the steps above manually.

Good luck with your hackathon submission!
