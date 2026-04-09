#!/bin/bash

# Project Aegis - Automated Startup Script
# This script starts both the backend and frontend servers

set -e

AEGIS_ROOT="/home/pranjay/workspace/Projects/Aegis"
BACKEND_DIR="$AEGIS_ROOT/no1"
FRONTEND_DIR="$AEGIS_ROOT/no"

echo "🚀 Project Aegis - Starting Infrastructure"
echo "=========================================="

# Kill any existing processes
echo "🧹 Cleaning up old processes..."
pkill -f "python server.py" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 1

# Start Backend
echo ""
echo "▶️  Starting Backend (port 8000)..."
cd "$BACKEND_DIR"
./.venv/bin/python server.py &
BACKEND_PID=$!
sleep 3

# Verify backend is running
if ! curl -s http://localhost:8000/ > /dev/null; then
    echo "❌ Backend failed to start on port 8000"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi
echo "✅ Backend running (PID: $BACKEND_PID)"

# Start Frontend
echo ""
echo "▶️  Starting Frontend (port 5173)..."
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
sleep 3
echo "✅ Frontend running (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "🎉 Project Aegis is ready!"
echo ""
echo "📱 Access the dashboard:"
echo "   http://localhost:5173/working-soon.html"
echo ""
echo "📊 API Endpoint:"
echo "   http://localhost:8000/api/process"
echo ""
echo "⏹️  To stop servers, press Ctrl+C"
echo "=========================================="

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
