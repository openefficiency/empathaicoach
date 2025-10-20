#!/bin/bash

# R2C2 Voice Coach - Render.com Deployment Helper
# This script helps you deploy to Render.com + Vercel

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}======================================================================${NC}"
echo -e "${MAGENTA}🚀 R2C2 Voice Coach - Render.com Deployment${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

echo -e "${CYAN}This script will help you deploy to Render.com + Vercel${NC}"
echo ""

# Check prerequisites
echo -e "${CYAN}Checking prerequisites...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js is installed${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm is installed${NC}"

# Check if .env exists
if [ ! -f "server/.env" ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo ""
    echo "Please create server/.env with your API keys:"
    echo ""
    echo "DAILY_API_KEY=your_daily_api_key_here"
    echo "GOOGLE_API_KEY=your_google_gemini_api_key_here"
    echo "DATABASE_PATH=./data/r2c2_coach.db"
    echo ""
    read -p "Press Enter after creating the .env file..."
fi

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${MAGENTA}Step 1: Backend Deployment Instructions${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

echo -e "${CYAN}Follow these steps to deploy your backend to Render.com:${NC}"
echo ""
echo "1. Go to https://render.com and sign up (free)"
echo ""
echo "2. Click 'New +' → 'Web Service'"
echo ""
echo "3. Connect your GitHub repository or use 'Deploy from Git URL'"
echo ""
echo "4. Configure your service:"
echo -e "   ${YELLOW}Name:${NC} r2c2-voice-coach-backend"
echo -e "   ${YELLOW}Region:${NC} Choose closest to you"
echo -e "   ${YELLOW}Branch:${NC} main"
echo -e "   ${YELLOW}Root Directory:${NC} server"
echo -e "   ${YELLOW}Runtime:${NC} Python 3"
echo -e "   ${YELLOW}Build Command:${NC} pip install -r requirements.txt"
echo -e "   ${YELLOW}Start Command:${NC} python bot.py --transport daily"
echo ""
echo "5. Add Environment Variables (click 'Advanced' → 'Add Environment Variable'):"
echo ""

# Read .env file and display
if [ -f "server/.env" ]; then
    echo -e "${GREEN}Your environment variables from server/.env:${NC}"
    echo ""
    while IFS= read -r line; do
        # Skip comments and empty lines
        if [[ ! "$line" =~ ^#.*$ ]] && [[ -n "$line" ]]; then
            echo "   $line"
        fi
    done < "server/.env"
    echo ""
else
    echo -e "   ${YELLOW}DAILY_API_KEY${NC}=your_daily_api_key"
    echo -e "   ${YELLOW}GOOGLE_API_KEY${NC}=your_gemini_api_key"
    echo -e "   ${YELLOW}DATABASE_PATH${NC}=./data/r2c2_coach.db"
    echo -e "   ${YELLOW}API_PORT${NC}=7860"
    echo -e "   ${YELLOW}API_HOST${NC}=0.0.0.0"
    echo ""
fi

echo "6. Click 'Create Web Service' and wait for deployment"
echo ""
echo "7. Once deployed, copy your Render URL (e.g., https://r2c2-voice-coach-backend.onrender.com)"
echo ""

read -p "Press Enter when your backend is deployed and you have the URL..."

echo ""
echo "Enter your Render backend URL (without /start):"
read -p "URL: " BACKEND_URL

# Remove trailing slash if present
BACKEND_URL=${BACKEND_URL%/}

echo ""
echo -e "${GREEN}✓ Backend URL: $BACKEND_URL${NC}"

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${MAGENTA}Step 2: Frontend Deployment to Vercel${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

cd client

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${CYAN}Installing Vercel CLI...${NC}"
    npm install -g vercel
    echo -e "${GREEN}✓ Vercel CLI installed${NC}"
fi

# Check if logged in
echo -e "${CYAN}Checking Vercel authentication...${NC}"
if ! vercel whoami &> /dev/null; then
    echo -e "${YELLOW}⚠ Not logged in to Vercel${NC}"
    echo ""
    echo "Please login to Vercel:"
    vercel login
    
    if ! vercel whoami &> /dev/null; then
        echo -e "${RED}✗ Login failed${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Authenticated with Vercel${NC}"

# Create/update .env.local
echo ""
echo -e "${CYAN}Creating .env.local with your backend URL...${NC}"

cat > .env.local << EOF
BOT_START_URL="$BACKEND_URL/start"
BOT_START_PUBLIC_API_KEY=""
NEXT_PUBLIC_API_BASE_URL="$BACKEND_URL"
NEXT_PUBLIC_ENABLE_EMOTION_VIZ=true
NEXT_PUBLIC_ENABLE_PLAN_EDITING=true
NEXT_PUBLIC_ENABLE_SESSION_EXPORT=true
NEXT_PUBLIC_DEBUG_MODE=false
NEXT_PUBLIC_AUTO_SCROLL_TRANSCRIPT=true
EOF

echo -e "${GREEN}✓ Created .env.local${NC}"

# Install dependencies
echo ""
echo -e "${CYAN}Installing frontend dependencies...${NC}"
npm install
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Deploy to Vercel
echo ""
echo -e "${CYAN}Deploying to Vercel...${NC}"
echo ""
echo "When prompted:"
echo "  - Set up and deploy? Yes"
echo "  - Which scope? Choose your account"
echo "  - Link to existing project? No"
echo "  - Project name? r2c2-voice-coach (or your choice)"
echo "  - Directory? ./"
echo "  - Override settings? No"
echo ""
read -p "Press Enter to continue with deployment..."

if vercel --prod; then
    echo -e "${GREEN}✓ Frontend deployed to Vercel${NC}"
else
    echo -e "${RED}✗ Failed to deploy to Vercel${NC}"
    exit 1
fi

# Get deployment URL
VERCEL_URL=$(vercel ls 2>/dev/null | grep "r2c2-voice-coach" | head -1 | awk '{print $2}' || echo "")

if [ -z "$VERCEL_URL" ]; then
    echo ""
    echo -e "${YELLOW}⚠ Could not automatically retrieve Vercel URL${NC}"
    echo "Please check your Vercel dashboard for the deployment URL"
    read -p "Enter your Vercel URL: " VERCEL_URL
fi

cd ..

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo -e "${CYAN}Your R2C2 Voice Coach is now live!${NC}"
echo ""
echo -e "${YELLOW}Backend (Render.com):${NC}"
echo -e "  URL: ${GREEN}$BACKEND_URL${NC}"
echo -e "  Bot Start: ${GREEN}$BACKEND_URL/start${NC}"
echo ""
echo -e "${YELLOW}Frontend (Vercel):${NC}"
echo -e "  Live URL: ${GREEN}https://$VERCEL_URL${NC}"
echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${MAGENTA}Next Steps:${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo "1. ${CYAN}Test your deployment:${NC}"
echo "   Open: https://$VERCEL_URL"
echo "   Click 'Start Session' and test the voice interaction"
echo ""
echo "2. ${CYAN}Monitor your deployment:${NC}"
echo "   Render: https://dashboard.render.com"
echo "   Vercel: https://vercel.com/dashboard"
echo ""
echo "3. ${CYAN}If backend is sleeping (Render free tier):${NC}"
echo "   First request may take 30 seconds to wake up"
echo "   Subsequent requests will be fast"
echo ""
echo "4. ${CYAN}Prepare hackathon submission:${NC}"
echo "   - Record a demo video"
echo "   - Update README with live URL"
echo "   - Test all features"
echo "   - Submit to hackathon!"
echo ""
echo -e "${GREEN}Good luck with your hackathon! 🚀${NC}"
echo ""

# Save deployment info
cat > DEPLOYMENT_INFO.txt << EOF
R2C2 Voice Coach - Deployment Information
==========================================

Deployment Date: $(date)
Deployment Method: Render.com + Vercel

Backend (Render.com):
  URL: $BACKEND_URL
  Bot Start: $BACKEND_URL/start
  Dashboard: https://dashboard.render.com
  
  Note: Free tier sleeps after 15 min of inactivity
  First request after sleep takes ~30 seconds

Frontend (Vercel):
  Live URL: https://$VERCEL_URL
  Dashboard: https://vercel.com/dashboard
  
  Commands:
    - View logs: cd client && vercel logs
    - Redeploy: cd client && vercel --prod
    - Set env var: cd client && vercel env add VARIABLE_NAME production

Quick Test:
  1. Open: https://$VERCEL_URL
  2. Click "Start Session"
  3. Allow microphone permissions
  4. Enter sample feedback
  5. Start coaching session

Troubleshooting:
  - Backend issues: Check Render dashboard logs
  - Frontend issues: Check Vercel logs and browser console
  - Connection issues: Verify API keys in Render environment variables
  - Slow first request: Backend is waking from sleep (normal on free tier)

Support:
  - Render Docs: https://render.com/docs
  - Vercel Docs: https://vercel.com/docs
  - Project README: See README.md
  - Simple Deployment Guide: See SIMPLE_DEPLOYMENT.md
EOF

echo -e "${GREEN}✓ Deployment info saved to DEPLOYMENT_INFO.txt${NC}"
echo ""
