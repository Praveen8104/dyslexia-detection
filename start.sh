#!/bin/bash
# =============================================================
# DyslexAI - Start both servers with one command
# Usage: ./start.sh
# =============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Kill any existing processes on our ports
lsof -ti:5001 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true

echo "=========================================="
echo "  Starting DyslexAI"
echo "=========================================="
echo ""

# Start backend
echo -e "${YELLOW}Starting backend server...${NC}"
cd backend
source venv/bin/activate
python3 run.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${YELLOW}Starting frontend server...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

sleep 2

echo ""
echo -e "${GREEN}=========================================="
echo "  Both servers are running!"
echo "==========================================${NC}"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://127.0.0.1:5001"
echo ""
echo "  Press Ctrl+C to stop both servers"
echo ""

# Trap Ctrl+C to kill both processes
trap "echo ''; echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

# Wait for either process to exit
wait
