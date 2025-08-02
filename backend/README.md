# AI Investment Advisory API (FastAPI Backend)

Clean Architecture implementation of the AI Investment Advisory System backend using FastAPI.

## Architecture Overview

```
backend/
├── api/                    # API Layer (Controllers)
│   ├── routes/            # FastAPI route handlers
│   └── dependencies/      # Dependency injection
├── application/           # Application Layer (Use Cases)
│   ├── dtos/             # Data Transfer Objects
│   ├── services/         # Application services
│   └── use_cases/        # Business use cases
├── domain/               # Domain Layer (Entities & Business Logic)
│   ├── entities/         # Domain entities
│   ├── repositories/     # Repository interfaces
│   └── services/         # Domain services
├── infrastructure/       # Infrastructure Layer
│   ├── cache/           # Redis cache implementation
│   ├── database/        # PostgreSQL implementation
│   └── repositories/    # Repository implementations
└── core/                # Core utilities and configuration
```

## Setup Instructions

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 7+
- Virtual environment (conda or venv)

### Installation

1. Create and activate virtual environment:
```bash
conda create -n stock-backend python=3.12
conda activate stock-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Set up PostgreSQL database:
```bash
createdb stock_db
```

5. Run database migrations:
```bash
alembic upgrade head
```

### Running the Application

Development mode:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Key Features

- **Clean Architecture**: Separation of concerns with clearly defined layers
- **Async/Await**: Fully asynchronous operations for better performance
- **Type Safety**: Full type hints with Pydantic models
- **Database**: PostgreSQL with SQLAlchemy ORM (async)
- **Caching**: Redis for performance optimization
- **AI Integration**: Supports both OpenAI direct calls and legacy Streamlit agents
- **Dependency Injection**: Clean dependency management with FastAPI
- **Health Checks**: Comprehensive health and readiness endpoints

## Configuration

Key environment variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/stock_db

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your_openai_key
USE_STREAMLIT_AGENTS=true  # Use legacy agents during migration

# Security
SECRET_KEY=your_secret_key_minimum_32_chars

# Feature Flags
ENABLE_CACHING=true
ENABLE_BACKGROUND_ANALYSIS=true
```

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=. --cov-report=html
```

## Development

Format code:
```bash
black .
```

Lint code:
```bash
ruff check .
```

Type checking:
```bash
mypy .
```

## API Endpoints

### Health Checks
- `GET /api/health/` - Basic health check
- `GET /api/health/ready` - Readiness check
- `GET /api/health/live` - Liveness check

### Stock Information
- `GET /api/stocks/search` - Search stocks
- `GET /api/stocks/{ticker}` - Get stock details
- `GET /api/stocks/{ticker}/price-history` - Get price history
- `GET /api/stocks/trending` - Get trending stocks

### Analysis
- `POST /api/analysis/` - Create new analysis
- `GET /api/analysis/{session_id}` - Get analysis results
- `GET /api/analysis/{session_id}/progress` - Get analysis progress
- `GET /api/analysis/` - List analyses

## Migration from Streamlit

The backend is designed to support gradual migration from the Streamlit application:

1. **Streamlit Agent Adapter**: Wraps existing Streamlit agents for use in FastAPI
2. **Feature Flag**: `USE_STREAMLIT_AGENTS` controls whether to use legacy agents
3. **Shared Database Models**: Compatible with existing data structures
4. **API Gateway Pattern**: Frontend can gradually switch from Streamlit to API calls

## Deployment

For production deployment:

1. Use environment-specific `.env` files
2. Run with multiple workers: `--workers 4`
3. Use a process manager like systemd or supervisor
4. Place behind a reverse proxy (nginx/caddy)
5. Enable HTTPS
6. Set up monitoring (Prometheus/Grafana)

## License

Proprietary - All rights reserved