#!/bin/bash
# Start FastAPI Backend Server

echo "🚀 Starting FastAPI Backend Server..."

# Check if we're using conda
if command -v conda &> /dev/null; then
    echo "Using conda environment 'stock'..."
    conda activate stock
else
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Check if PostgreSQL is running (optional)
echo "Checking database connection..."
if command -v pg_isready &> /dev/null; then
    if ! pg_isready -h localhost -p 5432; then
        echo "⚠️  PostgreSQL is not running. Please start PostgreSQL first."
        echo "   On macOS: brew services start postgresql"
        echo "   On Ubuntu: sudo systemctl start postgresql"
    fi
fi

# Skip migrations if database is not available
if [ -f "backend/.env" ]; then
    echo "Environment file found."
else
    echo "⚠️  No .env file found in backend/. Database migrations will be skipped."
fi

# Start FastAPI server
echo "Starting FastAPI server on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
cd backend
PYTHONPATH=/Users/hojinlee/Desktop/Develop/Deploy/stock/backend uvicorn main:app --reload --host 0.0.0.0 --port 8000