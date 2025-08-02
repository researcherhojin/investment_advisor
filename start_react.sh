#!/bin/bash
# Start React Frontend

echo "🎨 Starting React Frontend..."

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory not found!"
    echo ""
    echo "React frontend has not been set up yet."
    echo "The system is currently using Streamlit as the frontend."
    echo ""
    echo "To run the current Streamlit interface:"
    echo "  streamlit run main.py"
    echo ""
    echo "To create a React frontend (optional for future migration):"
    echo "  npx create-react-app frontend --template typescript"
    echo ""
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start React development server
echo "Starting React development server on http://localhost:3000"
npm start