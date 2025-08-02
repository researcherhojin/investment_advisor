#!/bin/bash

# Run Tests Script
# Execute all tests with coverage reporting

set -e  # Exit on error

echo "🧪 Running AI Investment Advisory API Tests..."
echo "============================================"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: No virtual environment detected."
    echo "   It's recommended to run tests in a virtual environment."
    echo ""
fi

# Set test environment variables
export ENVIRONMENT=testing
export DATABASE_URL=postgresql+asyncpg://test_user:test_password@localhost:5432/test_stock_db
export REDIS_URL=redis://localhost:6379/1
export OPENAI_API_KEY=test_key
export SECRET_KEY=test_secret_key_for_testing_only_32_chars
export USE_STREAMLIT_AGENTS=false

# Create test database if it doesn't exist
echo "📦 Setting up test database..."
createdb test_stock_db 2>/dev/null || echo "Test database already exists"

# Run different test suites
if [ "$1" == "unit" ]; then
    echo "🔍 Running unit tests only..."
    pytest tests/unit -v -m unit
elif [ "$1" == "integration" ]; then
    echo "🔗 Running integration tests only..."
    pytest tests/integration -v -m integration
elif [ "$1" == "coverage" ]; then
    echo "📊 Running all tests with detailed coverage..."
    pytest --cov=. \
           --cov-branch \
           --cov-report=term-missing:skip-covered \
           --cov-report=html \
           --cov-report=xml \
           --cov-fail-under=80 \
           -v
    echo ""
    echo "📈 Coverage report generated in htmlcov/index.html"
elif [ "$1" == "watch" ]; then
    echo "👀 Running tests in watch mode..."
    pytest-watch -- -v
elif [ "$1" == "quick" ]; then
    echo "⚡ Running quick tests (no coverage)..."
    pytest -v --tb=short
else
    echo "🚀 Running all tests..."
    pytest -v
fi

echo ""
echo "✅ Test run completed!"

# Clean up
if [ "$CLEANUP_TEST_DB" == "true" ]; then
    echo "🧹 Cleaning up test database..."
    dropdb test_stock_db 2>/dev/null || true
fi