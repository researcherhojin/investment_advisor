# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this AI Investment Advisory System.

## Project Overview

AI-powered investment advisory system for analyzing US and Korean stocks using multiple specialized AI agents. Currently transitioning from Streamlit to React + FastAPI architecture for better scalability and professional UI/UX.

## Development Environment

### Current Stack (Legacy)
- **Backend**: Python 3.12, Streamlit
- **AI**: OpenAI GPT-4, LangChain agents
- **Data**: Yahoo Finance, Alpha Vantage API
- **UI**: Streamlit with professional CSS themes

### Target Stack (Migration)
- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: FastAPI + Python 3.12
- **Database**: PostgreSQL + Redis
- **Deployment**: Docker containers
- **PWA**: Service workers, offline capability

## Common Development Commands

### Current System
```bash
# Setup environment
conda create -n stock python=3.12
conda activate stock
pip install -r requirements.txt

# Run application
streamlit run main.py

# Testing and quality
python -m pytest investment_advisor/tests/
ruff check .
mypy investment_advisor/

# Cache management
rm -rf .cache/

# Quick debugging
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG
```

### Docker Development (In Progress)
```bash
# Build development environment
docker-compose -f docker-compose.dev.yml up --build

# Frontend development
cd frontend && npm run dev

# Backend development
cd backend && uvicorn main:app --reload

# Database operations
docker-compose exec postgres psql -U stock_user -d stock_db
```

## Project Architecture

### Current Module Structure
```
investment_advisor/
├── agents/          # AI analysis agents (Company, Industry, Technical, etc.)
├── analysis/        # Core analysis engines (technical, fundamental)
├── data/           # Data fetchers (Yahoo Finance, Alpha Vantage)
├── ui/             # Streamlit UI components and styling
└── utils/          # Configuration, caching, utilities
```

### Target Architecture (Clean Architecture)
```
backend/
├── domain/         # Business logic and entities
├── application/    # Use cases and services
├── infrastructure/ # External services, databases
└── api/           # FastAPI routes and dependencies

frontend/
├── src/
│   ├── components/ # Reusable UI components
│   ├── pages/     # Page components
│   ├── hooks/     # Custom React hooks
│   ├── services/  # API communication
│   └── utils/     # Frontend utilities
```

## Key Development Guidelines

### Code Quality
- Follow Clean Code principles
- Use dependency injection
- Implement proper error handling
- Add comprehensive logging
- Write unit and integration tests

### Performance
- Use caching strategically (15min TTL for data)
- Implement lazy loading for UI components
- Use background jobs for heavy analysis
- Optimize database queries

### Security
- Never commit API keys or secrets
- Use environment variables for configuration
- Implement rate limiting
- Validate all user inputs
- Use HTTPS in production

## Common Tasks

### Adding New Analysis Agent
1. Create new agent class in `investment_advisor/agents/`
2. Inherit from `InvestmentAgent` base class
3. Implement `_run()` method with analysis logic
4. Add agent to decision system in `analysis/decision_system.py`
5. Update UI to display agent results

### Adding New Data Source
1. Create fetcher class in `investment_advisor/data/`
2. Inherit from `StockDataFetcher` base class
3. Implement required methods (fetch_price_history, etc.)
4. Add caching support
5. Update configuration options

### UI/UX Improvements
- Use professional color palette in `ui/styles.py`
- Follow glassmorphism design principles
- Implement responsive design
- Add loading states and error handling
- Use consistent typography and spacing

## Debugging and Troubleshooting

### Common Issues
1. **Yahoo Finance Rate Limiting**: Enable caching, add request delays
2. **OpenAI API Errors**: Check API key validity and rate limits
3. **Memory Issues**: Clear cache, optimize data structures
4. **UI Performance**: Use progressive loading, lazy components

### Logging
- Use structured logging with appropriate levels
- Filter duplicate messages (max 3 occurrences)
- Suppress third-party library noise
- Include request IDs for tracing

## Migration Progress

### Phase 1: Infrastructure (Current)
- [x] Clean up legacy files
- [x] Consolidate documentation
- [ ] Set up Docker development environment
- [ ] Initialize React + FastAPI projects
- [ ] Database schema design

### Phase 2: Backend Migration
- [ ] Implement Clean Architecture
- [ ] Migrate AI agents to FastAPI
- [ ] Set up background job processing
- [ ] Implement caching layer with Redis

### Phase 3: Frontend Development
- [ ] Create React component library
- [ ] Implement Bloomberg Terminal-style UI
- [ ] Add PWA capabilities
- [ ] Real-time data streaming

### Phase 4: Deployment & Optimization
- [ ] Production Docker setup
- [ ] CI/CD pipeline
- [ ] Performance monitoring
- [ ] Load testing and optimization

## Testing Strategy

### Current Testing
```bash
# Run all tests
python -m pytest investment_advisor/tests/ -v

# Test specific component
python -m pytest investment_advisor/tests/test_agents.py

# Test with coverage
pytest --cov=investment_advisor
```

### Target Testing (React + FastAPI)
```bash
# Backend tests
pytest backend/tests/

# Frontend tests
cd frontend && npm test

# Integration tests
docker-compose -f docker-compose.test.yml up
```

## Environment Variables

### Required
- `OPENAI_API_KEY`: OpenAI API key for AI agents
- `DATABASE_URL`: PostgreSQL connection string (future)
- `REDIS_URL`: Redis connection string (future)

### Optional
- `ALPHA_VANTAGE_API_KEY`: Backup data source
- `DEBUG_MODE`: Enable debug logging
- `USE_CACHE`: Enable/disable caching
- `RATE_LIMIT_ENABLED`: Enable API rate limiting

## Performance Targets

### Current System
- Page load: < 3s
- Analysis time: < 30s
- Cache hit ratio: > 80%

### Target System
- Initial load: < 1s
- Subsequent pages: < 500ms
- Real-time updates: < 100ms latency
- API response: < 200ms average

## Notes for Claude Code

- Always run tests after making changes
- Use the existing caching system to avoid API rate limits
- Follow the established error handling patterns
- Check TROUBLESHOOTING.md for common issues
- The system is in active migration - respect both current and target architectures
- Prioritize Clean Code principles and professional UI/UX standards