#!/bin/bash

echo "🚀 Starting Docker build and push..."
echo ""

# Build and push Docker image
python3 -m pipecatcloud docker build-push r2c2-voice-coach --registry dockerhub

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Docker build and push completed successfully!"
    echo ""
    echo "Next step: Deploy to Pipecat Cloud"
    echo "Run: python3 -m pipecatcloud deploy"
else
    echo ""
    echo "❌ Docker build failed. Please check the errors above."
    exit 1
fi
