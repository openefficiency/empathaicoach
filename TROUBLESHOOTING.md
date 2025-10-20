# 🔧 R2C2 Voice Coach - Troubleshooting Guide

## Quick Diagnostics

### Check System Status

```bash
# Backend status
cd server
uv run pcc status r2c2-coach

# Frontend status
cd client
vercel ls

# View backend logs
cd server
uv run pcc logs r2c2-coach --follow

# View frontend logs
cd client
vercel logs
```

---

## Common Issues & Solutions

### 🔴 Backend Deployment Issues

#### Issue: "pipecat-cli not found"

**Symptoms:**
```
command not found: pcc
```

**Solution:**
```bash
# Install Pipecat CLI
uv tool install pipecat-cli

# Verify installation
uv tool list

# If still not working, try:
uv tool install --force pipecat-cli
```

---

#### Issue: "Not authenticated with Pipecat Cloud"

**Symptoms:**
```
Error: Not logged in
```

**Solution:**
```bash
# Login to Pipecat Cloud
uv run pcc login

# Follow the browser authentication flow

# Verify login
uv run pcc whoami
```

---

#### Issue: "Docker build failed"

**Symptoms:**
```
Error: Docker daemon not running
Error: Failed to build image
```

**Solutions:**

1. **Check Docker is running:**
```bash
docker ps
```

2. **Start Docker:**
   - macOS: Open Docker Desktop
   - Linux: `sudo systemctl start docker`
   - Windows: Start Docker Desktop

3. **Check Docker permissions:**
```bash
# Linux only
sudo usermod -aG docker $USER
# Log out and back in
```

4. **Clean Docker cache:**
```bash
docker system prune -a
```

5. **Rebuild:**
```bash
cd server
uv run pcc docker build-push
```

---

#### Issue: "Secrets upload failed"

**Symptoms:**
```
Error: Failed to upload secrets
Error: Invalid secret format
```

**Solutions:**

1. **Check .env file format:**
```bash
# Correct format (no spaces around =)
DAILY_API_KEY=abc123
GOOGLE_API_KEY=xyz789

# Incorrect format
DAILY_API_KEY = abc123  # ❌ spaces
DAILY_API_KEY="abc123"  # ❌ quotes (unless needed)
```

2. **Verify .env exists:**
```bash
cd server
ls -la .env
cat .env  # Check contents
```

3. **Re-upload secrets:**
```bash
uv run pcc secrets set r2c2-coach --file .env

# Or upload individually
uv run pcc secrets set r2c2-coach DAILY_API_KEY=your_key
```

4. **Verify secrets:**
```bash
uv run pcc secrets list
uv run pcc secrets get r2c2-coach DAILY_API_KEY
```

---

#### Issue: "Agent deployment failed"

**Symptoms:**
```
Error: Deployment failed
Error: Health check failed
```

**Solutions:**

1. **Check deployment logs:**
```bash
uv run pcc logs r2c2-coach --follow
```

2. **Verify secrets are set:**
```bash
uv run pcc secrets list
```

3. **Check agent status:**
```bash
uv run pcc status r2c2-coach
```

4. **Redeploy:**
```bash
uv run pcc deploy
```

5. **If still failing, check for errors in code:**
```bash
# Test locally first
cd server
uv sync
uv run bot.py --transport daily
```

---

#### Issue: "Bot not responding"

**Symptoms:**
- Frontend connects but no response
- Timeout errors
- Silent bot

**Solutions:**

1. **Check agent is running:**
```bash
uv run pcc status r2c2-coach
# Should show "running"
```

2. **Check logs for errors:**
```bash
uv run pcc logs r2c2-coach --tail 100
```

3. **Verify API keys:**
```bash
# Check Daily.co key
uv run pcc secrets get r2c2-coach DAILY_API_KEY

# Check Gemini key
uv run pcc secrets get r2c2-coach GOOGLE_API_KEY
```

4. **Test API keys:**
```bash
# Test Daily.co key
curl -H "Authorization: Bearer YOUR_DAILY_KEY" \
  https://api.daily.co/v1/rooms

# Test Gemini key
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=YOUR_GEMINI_KEY"
```

5. **Restart agent:**
```bash
uv run pcc deploy
```

---

### 🔴 Frontend Deployment Issues

#### Issue: "Vercel CLI not found"

**Symptoms:**
```
command not found: vercel
```

**Solution:**
```bash
# Install Vercel CLI globally
npm install -g vercel

# Verify installation
vercel --version

# If permission error on macOS/Linux:
sudo npm install -g vercel
```

---

#### Issue: "Not authenticated with Vercel"

**Symptoms:**
```
Error: Not logged in
```

**Solution:**
```bash
# Login to Vercel
vercel login

# Follow email verification

# Verify login
vercel whoami
```

---

#### Issue: "Build failed on Vercel"

**Symptoms:**
```
Error: Build failed
Error: Module not found
```

**Solutions:**

1. **Check build logs in Vercel dashboard**

2. **Test build locally:**
```bash
cd client
npm install
npm run build
```

3. **Common fixes:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Update dependencies
npm update

# Check for TypeScript errors
npm run build
```

4. **Verify environment variables:**
```bash
# List env vars
vercel env ls

# Add missing vars
vercel env add VARIABLE_NAME production
```

---

#### Issue: "Environment variables not working"

**Symptoms:**
- Bot URL not found
- Features not enabled
- API calls failing

**Solutions:**

1. **Check .env.local:**
```bash
cd client
cat .env.local
```

2. **Verify Vercel environment variables:**
```bash
vercel env ls
```

3. **Add/update variables:**
```bash
# Add new variable
vercel env add BOT_START_URL production

# Update existing (remove and re-add)
vercel env rm BOT_START_URL production
vercel env add BOT_START_URL production
```

4. **Redeploy after env changes:**
```bash
vercel --prod
```

5. **Check variable names:**
   - Client-side vars MUST start with `NEXT_PUBLIC_`
   - Server-side vars don't need prefix

---

### 🔴 Connection Issues

#### Issue: "WebRTC connection failed"

**Symptoms:**
```
Error: Failed to connect to Daily room
Error: ICE connection failed
```

**Solutions:**

1. **Check Daily.co API key:**
```bash
# Verify key is valid
curl -H "Authorization: Bearer YOUR_DAILY_KEY" \
  https://api.daily.co/v1/rooms
```

2. **Check Daily.co account:**
   - Login to https://dashboard.daily.co/
   - Verify account is active
   - Check available minutes

3. **Browser issues:**
   - Use Chrome (best WebRTC support)
   - Allow microphone permissions
   - Disable browser extensions
   - Try incognito mode

4. **Network issues:**
   - Check firewall settings
   - Try different network
   - Disable VPN temporarily

5. **Check browser console:**
   - Open DevTools (F12)
   - Look for WebRTC errors
   - Check Network tab for failed requests

---

#### Issue: "Microphone not working"

**Symptoms:**
- No audio detected
- Microphone permission denied
- Silent input

**Solutions:**

1. **Grant browser permissions:**
   - Click lock icon in address bar
   - Allow microphone access
   - Refresh page

2. **Check system microphone:**
   - macOS: System Preferences → Security & Privacy → Microphone
   - Windows: Settings → Privacy → Microphone
   - Linux: Check PulseAudio/ALSA settings

3. **Test microphone:**
```bash
# macOS
say "Testing microphone"

# Linux
arecord -d 5 test.wav && aplay test.wav
```

4. **Try different browser:**
   - Chrome (recommended)
   - Firefox
   - Edge

---

#### Issue: "High latency / Slow responses"

**Symptoms:**
- Long delays between speaking and response
- Choppy audio
- Timeouts

**Solutions:**

1. **Check internet connection:**
```bash
# Test speed
speedtest-cli

# Test latency
ping google.com
```

2. **Check Gemini API quota:**
   - Visit https://aistudio.google.com/
   - Check API usage
   - Verify not rate limited

3. **Check Pipecat Cloud status:**
```bash
uv run pcc status r2c2-coach
```

4. **Optimize settings:**
   - Close other applications
   - Use wired connection
   - Reduce video quality if using camera

---

### 🔴 Database Issues

#### Issue: "Database locked"

**Symptoms:**
```
Error: database is locked
Error: unable to open database file
```

**Solutions:**

1. **Close other connections:**
```bash
# Find processes using database
lsof | grep r2c2_coach.db

# Kill if needed
kill -9 <PID>
```

2. **Check file permissions:**
```bash
ls -la server/database/
chmod 644 server/database/r2c2_coach.db
```

3. **Restart application:**
```bash
uv run pcc deploy
```

---

#### Issue: "Database corruption"

**Symptoms:**
```
Error: database disk image is malformed
Error: unable to read database
```

**Solutions:**

1. **Backup database:**
```bash
cp server/database/r2c2_coach.db server/database/r2c2_coach.backup.db
```

2. **Try to repair:**
```bash
sqlite3 server/database/r2c2_coach.db "PRAGMA integrity_check;"
```

3. **If corrupted, restore from backup or recreate:**
```bash
# Remove corrupted database
rm server/database/r2c2_coach.db

# Redeploy (will create new database)
uv run pcc deploy
```

---

### 🔴 API Key Issues

#### Issue: "Invalid API key"

**Symptoms:**
```
Error: Invalid API key
Error: Unauthorized
Error: 401
```

**Solutions:**

1. **Verify Daily.co key:**
```bash
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.daily.co/v1/
```

2. **Verify Gemini key:**
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
```

3. **Check key format:**
   - Daily.co: Should start with `daily_`
   - Gemini: Should be a long alphanumeric string

4. **Regenerate keys:**
   - Daily.co: https://dashboard.daily.co/developers
   - Gemini: https://aistudio.google.com/app/apikey

5. **Update secrets:**
```bash
cd server
# Update .env file
uv run pcc secrets set r2c2-coach --file .env
uv run pcc deploy
```

---

### 🔴 Performance Issues

#### Issue: "Slow emotion detection"

**Symptoms:**
- Delayed emotion updates
- High CPU usage
- Laggy interface

**Solutions:**

1. **Check agent resources:**
```bash
uv run pcc status r2c2-coach
```

2. **Upgrade agent profile:**
   - Edit `server/pcc-deploy.toml`
   - Change `agent_profile = "agent-4x"`
   - Redeploy

3. **Optimize emotion detection:**
   - Reduce analysis window
   - Adjust detection frequency

---

## 🔍 Debugging Tools

### Backend Debugging

```bash
# View real-time logs
uv run pcc logs r2c2-coach --follow

# View last 100 lines
uv run pcc logs r2c2-coach --tail 100

# Check agent metrics
uv run pcc metrics r2c2-coach

# List active sessions
uv run pcc sessions r2c2-coach
```

### Frontend Debugging

```bash
# View deployment logs
vercel logs

# View build logs
vercel logs --output build

# Inspect deployment
vercel inspect <deployment-url>
```

### Browser Debugging

1. **Open DevTools (F12)**
2. **Check Console tab** for JavaScript errors
3. **Check Network tab** for failed requests
4. **Check Application tab** for storage issues

---

## 📞 Getting Help

### Self-Service Resources

1. **Documentation:**
   - DEPLOYMENT.md - Detailed deployment guide
   - HACKATHON_DEPLOYMENT.md - Quick deployment
   - README.md - Project overview

2. **Logs:**
   - Backend: `uv run pcc logs r2c2-coach --follow`
   - Frontend: `vercel logs`
   - Browser: DevTools Console

3. **Status Pages:**
   - Pipecat Cloud: Check dashboard
   - Vercel: Check dashboard
   - Daily.co: https://status.daily.co/

### Community Support

1. **Pipecat Discord:** https://discord.gg/pipecat
2. **Daily.co Community:** https://community.daily.co/
3. **Vercel Community:** https://github.com/vercel/vercel/discussions

### Emergency Fixes

If everything is broken:

```bash
# 1. Rollback backend
cd server
uv run pcc rollback r2c2-coach

# 2. Rollback frontend
cd client
vercel rollback

# 3. Check status
uv run pcc status r2c2-coach
vercel ls

# 4. Review logs
uv run pcc logs r2c2-coach --tail 200
vercel logs
```

---

## ✅ Health Check Checklist

Run this checklist to verify everything is working:

- [ ] Backend deployed: `uv run pcc status r2c2-coach`
- [ ] Frontend deployed: `vercel ls`
- [ ] Secrets uploaded: `uv run pcc secrets list`
- [ ] Environment variables set: `vercel env ls`
- [ ] Bot URL accessible: `curl <bot-url>`
- [ ] Frontend loads: Open in browser
- [ ] Microphone works: Test in browser
- [ ] Voice connection: Start a session
- [ ] AI responds: Speak and listen
- [ ] Emotions detected: Check visualization
- [ ] Phases transition: Complete a session
- [ ] Database saves: Check session history

---

## 🎯 Quick Fixes

### "It's not working!"

1. Check logs first
2. Verify API keys
3. Restart services
4. Clear cache
5. Try different browser

### "I changed something and now it's broken!"

1. Rollback changes
2. Check what you changed
3. Test locally first
4. Deploy incrementally

### "It worked yesterday!"

1. Check service status pages
2. Verify API quotas
3. Check for expired keys
4. Review recent changes

---

**Still stuck? Check DEPLOYMENT_INFO.txt for your specific deployment details.**
