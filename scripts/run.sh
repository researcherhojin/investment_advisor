#!/bin/bash

# AI Investment Advisor - Run Script

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 AI Investment Advisor - Starting Application"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run: ./setup_uv.sh"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env from .env.example"
        echo -e "${YELLOW}Please edit .env and add your OPENAI_API_KEY${NC}"
        exit 1
    fi
fi

# Check if OPENAI_API_KEY is set (with or without quotes)
if ! grep -q 'OPENAI_API_KEY=["'"'"']*sk-' .env; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY not configured in .env${NC}"
    echo "Please add your OpenAI API key to .env file"
    exit 1
fi

echo -e "${GREEN}✅ Environment ready${NC}"
echo ""
echo "Starting Streamlit application..."
echo "================================="
echo ""

# Run the application
streamlit run main.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false
