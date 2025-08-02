#!/bin/bash
# Start both React and FastAPI

echo "🚀 Starting AI Investment Advisory System..."
echo "=========================================="

# Function to kill processes on exit
cleanup() {
    echo "\n🛑 Stopping all services..."
    kill $FASTAPI_PID $REACT_PID 2>/dev/null
    exit
}

# Set up trap to call cleanup on script exit
trap cleanup EXIT INT TERM

# Start FastAPI in background
echo "\n1. Starting FastAPI Backend..."
./start_fastapi.sh &
FASTAPI_PID=$!

# Wait a bit for FastAPI to start
sleep 5

# Start React in background
echo "\n2. Starting React Frontend..."
./start_react.sh &
REACT_PID=$!

echo "\n=========================================="
echo "✅ All services started!"
echo ""
echo "📍 Access points:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Streamlit (legacy): streamlit run main.py"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="

# Wait for both processes
wait