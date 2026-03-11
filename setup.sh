#!/bin/bash
# =============================================================
# DyslexAI - One-Command Setup Script
# Run this after cloning the repo:
#   chmod +x setup.sh && ./setup.sh
# =============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  DyslexAI - Project Setup"
echo "=========================================="
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: python3 not found. Install Python 3.9+${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: node not found. Install Node.js 18+${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}ERROR: npm not found. Install Node.js 18+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
NODE_VERSION=$(node -v)
echo -e "${GREEN}Python: $PYTHON_VERSION${NC}"
echo -e "${GREEN}Node: $NODE_VERSION${NC}"
echo ""

# ---- Backend Setup ----
echo -e "${YELLOW}[1/4] Setting up backend virtual environment...${NC}"
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Created virtual environment"
else
    echo "  Virtual environment already exists"
fi

source venv/bin/activate
echo "  Activated venv"

echo -e "${YELLOW}[2/4] Installing Python dependencies...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}  Backend dependencies installed${NC}"

# Check for saved models
echo ""
if [ ! -f "saved_models/handwriting_model.keras" ] || [ ! -f "saved_models/speech_model.keras" ]; then
    echo -e "${RED}=========================================="
    echo "  IMPORTANT: ML Models Missing!"
    echo "==========================================${NC}"
    echo ""
    echo "Download the models from the shared Google Drive link"
    echo "and place them in: backend/saved_models/"
    echo ""
    echo "Required files:"
    echo "  - handwriting_model.keras (23 MB)"
    echo "  - speech_model.keras (1 MB)"
    echo ""
    echo "The app will still run without models (using heuristic"
    echo "analysis only), but accuracy will be lower."
    echo ""
else
    echo -e "${GREEN}  ML models found in saved_models/${NC}"
fi

# Create required directories
mkdir -p uploads/handwriting uploads/audio saved_models
echo "  Created upload directories"

deactivate
cd ..

# ---- Frontend Setup ----
echo ""
echo -e "${YELLOW}[3/4] Installing frontend dependencies...${NC}"
cd frontend
npm install --silent 2>/dev/null
echo -e "${GREEN}  Frontend dependencies installed${NC}"
cd ..

# ---- Done ----
echo ""
echo -e "${GREEN}=========================================="
echo "  Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "To start the app, open TWO terminal windows:"
echo ""
echo -e "${YELLOW}Terminal 1 (Backend):${NC}"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python3 run.py"
echo ""
echo -e "${YELLOW}Terminal 2 (Frontend):${NC}"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
