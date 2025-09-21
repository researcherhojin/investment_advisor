#!/bin/bash

# AI Investment Advisor - UV Setup Script
# This script sets up the development environment using uv package manager

set -e  # Exit on error

echo "🚀 AI Investment Advisor - UV 환경 설정"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."

    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install uv
        else
            curl -LsSf https://astral.sh/uv/install.sh | sh
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -LsSf https://astral.sh/uv/install.sh | sh
    else
        # Windows (Git Bash/WSL)
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    fi

    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.cargo/bin:"* ]]; then
        export PATH="$HOME/.cargo/bin:$PATH"
        echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
    fi

    print_status "uv installed successfully"
else
    print_status "uv is already installed: $(uv --version)"
fi

# Create Python virtual environment with uv
echo ""
echo "🐍 Setting up Python environment..."

# Remove old venv if exists
if [ -d ".venv" ]; then
    print_warning "Removing existing .venv directory..."
    rm -rf .venv
fi

# Create new virtual environment with Python 3.12
uv venv --python 3.12

print_status "Virtual environment created with Python 3.12"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."

# Install from pyproject.toml
echo "Installing base dependencies..."
uv pip install -e . --verbose

# Install dev dependencies
echo ""
echo "🛠️  Installing development dependencies..."
uv pip install -e ".[dev]" --verbose

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        print_status ".env file created from .env.example"
        print_warning "Please edit .env and add your API keys!"
    fi
fi

# Create cache directory
if [ ! -d ".cache" ]; then
    mkdir -p .cache
    print_status "Cache directory created"
fi

# Show Python and package info
echo ""
echo "📊 Environment Information:"
echo "=========================="
source .venv/bin/activate
echo "Python version: $(python --version)"
echo "uv version: $(uv --version)"
echo "Virtual environment: .venv"
echo ""

# List key installed packages
echo "Key packages installed:"
uv pip list | grep -E "(streamlit|openai|langchain|pandas|yfinance)" || true

echo ""
print_status "Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Configure your API keys in .env:"
echo "   OPENAI_API_KEY=your_key_here"
echo ""
echo "3. Run the application:"
echo "   streamlit run main.py"
echo ""
echo "🔧 Useful uv commands:"
echo "   uv pip install <package>     # Install a package"
echo "   uv pip list                  # List installed packages"
echo "   uv pip sync                  # Sync with pyproject.toml"
echo "   uv pip compile              # Create requirements.txt"
echo ""
