#!/bin/bash

# R2C2 Voice Coach - One-Click Hackathon Deployment Script
# This script automates the deployment process for hackathon submission

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Emojis
ROCKET="🚀"
CHECK="✓"
CROSS="✗"
WARN="⚠"
INFO="ℹ"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${MAGENTA}${ROCKET} R2C2 Voice Coach - Hackathon Deployment${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${CYAN}${INFO} $1${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}${WARN} $1${NC}"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed"
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
print_success "uv is installed"

# Check if node is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    echo "Install it from: https://nodejs.org/"
    exit 1
fi
print_success "Node.js is installed"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi
print_success "npm is installed"

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${MAGENTA}Step 1: Backend Deployment to Pipecat Cloud${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Check if .env exists
if [ ! -f "server/.env" ]; then
    print_warning ".env file not found in server directory"
    echo ""
    echo "Please create server/.env with your API keys:"
    echo ""
    echo "DAILY_API_KEY=your_daily_api_key_here"
    echo "GOOGLE_API_KEY=your_google_gemini_api_key_here"
    echo "DATABASE_PATH=./data/r2c2_coach.db"
    echo ""
    read -p "Press Enter after creating the .env file..."
    
    if [ ! -f "server/.env" ]; then
        print_error ".env file still not found. Exiting."
        exit 1
    fi
fi

print_success "Found .env file"

# Navigate to server directory
cd server

# Check if pipecatcloud is installed
print_status "Checking Pipecat Cloud CLI..."
if ! command -v pcc &> /dev/null; then
    print_status "Installing Pipecat Cloud CLI..."
    pip install pipecatcloud
    print_success "Pipecat Cloud CLI installed"
else
    print_success "Pipecat Cloud CLI already installed"
fi

# Check if logged in to Pipecat Cloud
print_status "Checking Pipecat Cloud authentication..."
if ! pcc whoami &> /dev/null; then
    print_warning "Not logged in to Pipecat Cloud"
    echo ""
    echo "Please login to Pipecat Cloud:"
    pcc login
    
    if ! pcc whoami &> /dev/null; then
        print_error "Login failed. Exiting."
        exit 1
    fi
fi
print_success "Authenticated with Pipecat Cloud"

# Upload secrets
print_status "Uploading secrets to Pipecat Cloud..."
if pcc secrets set r2c2-coach --file .env; then
    print_success "Secrets uploaded successfully"
else
    print_error "Failed to upload secrets"
    exit 1
fi

# Build Docker image
print_status "Building Docker image (this may take a few minutes)..."
if pcc docker build-push; then
    print_success "Docker image built and pushed"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Deploy agent
print_status "Deploying agent to Pipecat Cloud..."
if pcc deploy; then
    print_success "Agent deployed successfully"
else
    print_error "Failed to deploy agent"
    exit 1
fi

# Wait for deployment to be ready
print_status "Waiting for deployment to be ready..."
sleep 10

# Get agent info
print_status "Getting agent information..."
BOT_URL=$(pcc agent info r2c2-coach 2>/dev/null | grep -o 'https://api.pipecat.daily.co/v1/public/r2c2-coach/start' || echo "")

if [ -z "$BOT_URL" ]; then
    print_warning "Could not automatically retrieve bot URL"
    echo ""
    echo "Please run: uv run pcc agent info r2c2-coach"
    echo "And copy the bot URL"
    read -p "Enter your bot URL: " BOT_URL
fi

print_success "Bot URL: $BOT_URL"

# Navigate back to root
cd ..

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${MAGENTA}Step 2: Frontend Deployment to Vercel${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Navigate to client directory
cd client

# Check if .env.local exists, if not create it
if [ ! -f ".env.local" ]; then
    print_status "Creating .env.local file..."
    cat > .env.local << EOF
BOT_START_URL="$BOT_URL"
BOT_START_PUBLIC_API_KEY=""
NEXT_PUBLIC_API_BASE_URL="https://api.pipecat.daily.co/v1/public/r2c2-coach"
NEXT_PUBLIC_ENABLE_EMOTION_VIZ=true
NEXT_PUBLIC_ENABLE_PLAN_EDITING=true
NEXT_PUBLIC_ENABLE_SESSION_EXPORT=true
NEXT_PUBLIC_DEBUG_MODE=false
NEXT_PUBLIC_AUTO_SCROLL_TRANSCRIPT=true
EOF
    print_success "Created .env.local"
else
    print_status "Updating .env.local with bot URL..."
    # Update BOT_START_URL in existing .env.local
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|BOT_START_URL=.*|BOT_START_URL=\"$BOT_URL\"|" .env.local
    else
        sed -i "s|BOT_START_URL=.*|BOT_START_URL=\"$BOT_URL\"|" .env.local
    fi
    print_success "Updated .env.local"
fi

# Install dependencies
print_status "Installing frontend dependencies..."
if npm install; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    print_status "Installing Vercel CLI..."
    npm install -g vercel
    print_success "Vercel CLI installed"
fi

# Check if logged in to Vercel
print_status "Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    print_warning "Not logged in to Vercel"
    echo ""
    echo "Please login to Vercel:"
    vercel login
    
    if ! vercel whoami &> /dev/null; then
        print_error "Login failed. Exiting."
        exit 1
    fi
fi
print_success "Authenticated with Vercel"

# Deploy to Vercel
print_status "Deploying to Vercel..."
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
    print_success "Frontend deployed to Vercel"
else
    print_error "Failed to deploy to Vercel"
    exit 1
fi

# Get deployment URL
VERCEL_URL=$(vercel ls 2>/dev/null | grep "r2c2-voice-coach" | head -1 | awk '{print $2}' || echo "")

if [ -z "$VERCEL_URL" ]; then
    print_warning "Could not automatically retrieve Vercel URL"
    echo ""
    echo "Please check your Vercel dashboard for the deployment URL"
    read -p "Enter your Vercel URL: " VERCEL_URL
fi

# Navigate back to root
cd ..

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}${ROCKET} Deployment Complete!${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo -e "${CYAN}Your R2C2 Voice Coach is now live!${NC}"
echo ""
echo -e "${YELLOW}Backend (Pipecat Cloud):${NC}"
echo -e "  Bot URL: ${GREEN}$BOT_URL${NC}"
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
echo "   Backend logs: ${YELLOW}cd server && uv run pcc logs r2c2-coach --follow${NC}"
echo "   Vercel logs: ${YELLOW}cd client && vercel logs${NC}"
echo ""
echo "3. ${CYAN}Prepare hackathon submission:${NC}"
echo "   - Record a demo video"
echo "   - Update README with live URL"
echo "   - Test all features"
echo "   - Submit to hackathon!"
echo ""
echo -e "${GREEN}Good luck with your hackathon! ${ROCKET}${NC}"
echo ""

# Save deployment info
cat > DEPLOYMENT_INFO.txt << EOF
R2C2 Voice Coach - Deployment Information
==========================================

Deployment Date: $(date)

Backend (Pipecat Cloud):
  Bot URL: $BOT_URL
  Agent Name: r2c2-coach
  
  Commands:
    - View logs: cd server && uv run pcc logs r2c2-coach --follow
    - Check status: cd server && uv run pcc status r2c2-coach
    - Redeploy: cd server && uv run pcc deploy

Frontend (Vercel):
  Live URL: https://$VERCEL_URL
  
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
  - Backend issues: Check Pipecat Cloud logs
  - Frontend issues: Check Vercel logs and browser console
  - Connection issues: Verify API keys in secrets

Support:
  - Pipecat Docs: https://docs.pipecat.ai/
  - Vercel Docs: https://vercel.com/docs
  - Project README: See README.md
EOF

print_success "Deployment info saved to DEPLOYMENT_INFO.txt"
echo ""
