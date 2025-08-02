#!/bin/bash
# Start Streamlit Application

echo "🎨 Starting Streamlit Application..."

# Check if we're already in conda environment
if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
    echo "Already in conda environment: $CONDA_DEFAULT_ENV"
else
    # Check if we're using conda
    if command -v conda &> /dev/null; then
        echo "Conda detected. Please run: conda activate stock"
        echo "Then run this script again."
        exit 1
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
fi

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch .deps_installed
fi

# Set environment variables if .env exists
if [ -f ".env" ]; then
    echo "Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start Streamlit
echo "Starting Streamlit on http://localhost:8501"
streamlit run main.py