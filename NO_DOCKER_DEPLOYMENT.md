# 🚀 Fast Deployment Without Docker (10 minutes)

Since Docker build is taking too long, here's the fastest way to deploy for your hackathon.

## Option: Render.com (No Docker Required!)

Render.com builds from your GitHub repository directly - no Docker needed!

---

## Step 1: Push to GitHub (3 minutes)

Your code is already committed locally. Now push it to GitHub:

```bash
# 1. Create a new repository on GitHub
# Go to: https://github.com/new
# Name: r2c2-voice-coach
# Make it Public
# Don't initialize with README (you already have one)

# 2. Add GitHub as remote (replace YOUR_USERNAME)
cd r2c2-voice-coach
git remote add origin https://github.com/YOUR_USERNAME/r2c2-voice-coach.git

# 3. Push your code
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend to Render.com (5 minutes)

### 2.1 Sign Up for Render

1. Go to https://render.com
2. Click "Get Started" or "Sign Up"
3. Sign up with GitHub (easiest) or email

### 2.2 Create Web Service

1. Click "New +" → "Web Service"
2. Click "Connect account" to connect your GitHub
3. Select your `r2c2-voice-coach` repository
4. Click "Connect"

### 2.3 Configure Service

Fill in these settings:

```
Name: r2c2-voice-coach-backend
Region: Oregon (US West) or closest to you
Branch: main
Root Directory: server
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python bot.py --transport daily
Instance Type: Free
```

### 2.4 Add Environment Variables

Click "Advanced" → Scroll to "Environment Variables" → Add these:

```
DAILY_API_KEY = e5dd8a809058d2d681563ac4d58f242bc03ceeb91cf25ee776b772d5b43d0aac
GOOGLE_API_KEY = AIzaSyAY3H_bhXWnydY23P_uiSvOcMOzSZ5-GYk
DATABASE_PATH = ./data/r2c2_coach.db
API_PORT = 7860
API_HOST = 0.0.0.0
LOG_LEVEL = INFO
```

### 2.5 Deploy

1. Click "Create Web Service"
2. Wait 3-5 minutes for deployment
3. You'll see build logs in real-time
4. When it says "Live", your backend is ready!

### 2.6 Get Your Backend URL

After deployment, you'll see your URL at the top:
```
https://r2c2-voice-coach-backend.onrender.com
```

Your bot start endpoint is:
```
https://r2c2-voice-coach-backend.onrender.com/start
```

**Save this URL!**

---

## Step 3: Deploy Frontend to Vercel (2 minutes)

```bash
cd client

# Install Vercel CLI if needed
npm install -g vercel

# Login
vercel login

# Create .env.local with your Render URL
cat > .env.local << 'EOF'
BOT_START_URL="https://r2c2-voice-coach-backend.onrender.com/start"
NEXT_PUBLIC_API_BASE_URL="https://r2c2-voice-coach-backend.onrender.com"
NEXT_PUBLIC_ENABLE_EMOTION_VIZ=true
NEXT_PUBLIC_ENABLE_PLAN_EDITING=true
NEXT_PUBLIC_DEBUG_MODE=false
EOF

# Deploy
vercel --prod
```

When prompted:
- Set up and deploy? **Yes**
- Which scope? **Your account**
- Link to existing project? **No**
- Project name? **r2c2-voice-coach**
- Directory? **./  **
- Override settings? **No**

---

## Step 4: Test Your Deployment (1 minute)

1. Open your Vercel URL (shown after deployment)
2. Click "Start Session"
3. Allow microphone
4. Enter sample feedback
5. Start coaching!

---

## ✅ Complete Checklist

- [ ] Code pushed to GitHub
- [ ] Backend deployed to Render.com
- [ ] Environment variables added in Render
- [ ] Backend is "Live" on Render
- [ ] Frontend deployed to Vercel
- [ ] Tested the live application
- [ ] Recorded demo video
- [ ] Ready to submit!

---

## 🎯 Why This is Better for Hackathons

✅ **No Docker** - Render builds from source  
✅ **Faster** - 10 minutes total vs 30+ minutes  
✅ **Free** - Both Render and Vercel have free tiers  
✅ **Simple** - Just connect GitHub and deploy  
✅ **Reliable** - No complex build issues  

---

## 📝 Quick Commands

```bash
# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/r2c2-voice-coach.git
git push -u origin main

# Deploy frontend
cd client
vercel --prod
```

---

## ⚠️ Important Notes

### Render Free Tier

- Backend sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Subsequent requests are fast
- Perfect for demos and hackathons!

### For Your Demo

- Wake up the backend before your demo by visiting the URL
- Or upgrade to paid tier ($7/month) for always-on

---

## 🆘 Troubleshooting

### Backend build fails on Render

Check the build logs in Render dashboard. Common issues:

1. **Missing requirements.txt**
   ```bash
   cd server
   pip freeze > requirements.txt
   git add requirements.txt
   git commit -m "Add requirements.txt"
   git push
   ```

2. **Python version**
   - Render uses Python 3.7 by default
   - Add `runtime.txt` in server directory:
   ```
   python-3.12.0
   ```

### Frontend can't connect

- Verify BOT_START_URL in Vercel environment variables
- Check Render backend is "Live"
- Test backend URL directly: `curl https://your-backend.onrender.com/health`

---

**Ready to deploy? Follow the steps above!** 🚀

Total time: ~10 minutes from start to live application.
