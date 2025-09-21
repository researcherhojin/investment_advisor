# AI Investment Advisor - Makefile
# Convenient commands for development

.PHONY: help setup install run test lint clean docker-up docker-down

# Default target
help:
	@echo "AI Investment Advisor - Development Commands"
	@echo "==========================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Complete setup with uv"
	@echo "  make install        - Install dependencies"
	@echo "  make install-dev    - Install with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run            - Run Streamlit app"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linting (ruff)"
	@echo "  make format         - Format code (black)"
	@echo "  make typecheck      - Type checking (mypy)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      - Start Docker services"
	@echo "  make docker-down    - Stop Docker services"
	@echo "  make docker-logs    - View Docker logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Clean cache and temp files"
	@echo "  make clean-all      - Clean everything including venv"
	@echo "  make update-deps    - Update all dependencies"

# Setup with uv
setup:
	@echo "🚀 Setting up development environment with uv..."
	@bash setup_uv.sh

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@uv pip install -e .

install-dev:
	@echo "📦 Installing all dependencies including dev..."
	@uv pip install -e ".[dev]"

# Run the application
run:
	@echo "🚀 Starting AI Investment Advisor..."
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate && streamlit run main.py; \
	else \
		streamlit run main.py; \
	fi

run-debug:
	@echo "🐛 Starting in debug mode..."
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate && export DEBUG_MODE=true && export LOG_LEVEL=DEBUG && streamlit run main.py; \
	else \
		export DEBUG_MODE=true && export LOG_LEVEL=DEBUG && streamlit run main.py; \
	fi

# Testing
test:
	@echo "🧪 Running tests..."
	@pytest investment_advisor/tests/ -v

test-coverage:
	@echo "📊 Running tests with coverage..."
	@pytest investment_advisor/tests/ --cov=investment_advisor --cov-report=html

# Code quality
lint:
	@echo "🔍 Running linter..."
	@ruff check .

format:
	@echo "✨ Formatting code..."
	@black investment_advisor/
	@ruff check --fix .

typecheck:
	@echo "🔍 Running type checker..."
	@mypy investment_advisor/

# Docker commands
docker-up:
	@echo "🐳 Starting Docker containers..."
	@docker-compose -f docker-compose.dev.yml --profile legacy up -d

docker-down:
	@echo "🛑 Stopping Docker containers..."
	@docker-compose -f docker-compose.dev.yml down

docker-logs:
	@echo "📋 Viewing Docker logs..."
	@docker-compose -f docker-compose.dev.yml logs -f

docker-rebuild:
	@echo "🔨 Rebuilding Docker containers..."
	@docker-compose -f docker-compose.dev.yml build --no-cache

# Cleaning
clean:
	@echo "🧹 Cleaning cache and temporary files..."
	@rm -rf .cache/
	@rm -rf __pycache__/
	@rm -rf investment_advisor/__pycache__/
	@rm -rf investment_advisor/*/__pycache__/
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@rm -rf htmlcov/
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name ".DS_Store" -delete
	@echo "✅ Cleaned successfully"

clean-all: clean
	@echo "🧹 Cleaning everything including virtual environment..."
	@rm -rf .venv/
	@rm -rf venv/
	@rm -rf node_modules/
	@echo "✅ All cleaned"

# Dependency management
update-deps:
	@echo "📦 Updating dependencies..."
	@uv pip install --upgrade -e ".[dev]"
	@echo "✅ Dependencies updated"

freeze:
	@echo "📝 Creating requirements.txt..."
	@uv pip freeze > requirements.txt
	@echo "✅ requirements.txt created"

sync:
	@echo "🔄 Syncing with pyproject.toml..."
	@uv pip sync
	@echo "✅ Synced"

# Development shortcuts
dev: install-dev
	@echo "✅ Development environment ready"

check: lint typecheck test
	@echo "✅ All checks passed"

# Deployment
deploy-check:
	@echo "🚀 Checking deployment readiness..."
	@python -c "from investment_advisor.utils import get_config; get_config()"
	@echo "✅ Configuration valid"
	@echo "✅ Ready for deployment"

# Database
db-migrate:
	@echo "🗄️  Running database migrations..."
	@cd backend && alembic upgrade head

db-rollback:
	@echo "⏪ Rolling back last migration..."
	@cd backend && alembic downgrade -1

# Git shortcuts
commit-fixes:
	@echo "📝 Committing bug fixes..."
	@git add -A
	@git commit -m "fix: Streamlit deployment errors and improve UI/UX"

push:
	@echo "⬆️  Pushing to remote..."
	@git push origin main
