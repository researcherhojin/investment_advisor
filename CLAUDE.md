# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this AI Investment Advisory System.

## Project Overview

AI Investment Advisory System v0.2 (Beta) - A comprehensive stock analysis platform using 6 specialized AI agents (Company Analyst, Technical Analyst, Risk Manager, Industry Expert, Macroeconomist, Mediator) to analyze US and Korean stocks with real-time Yahoo Finance data.

## Quick Start Commands

```bash
# Setup environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run application
bash scripts/run.sh  # Or: streamlit run main.py

# Run with debug mode
export DEBUG_MODE=true && export LOG_LEVEL=DEBUG && streamlit run main.py

# Clear cache (if data issues)
rm -rf .cache/
```

## Project Structure

```
ai-investment-advisor/
├── investment_advisor/      # Core application modules
│   ├── agents/             # 6 AI analysis agents
│   ├── analysis/           # Decision system and orchestration
│   ├── data/              # Data fetchers (Yahoo, Stable, Simple)
│   ├── ui/                # Streamlit UI components
│   └── utils/             # Configuration and utilities
├── scripts/               # Shell scripts for automation
│   ├── quick_start.sh    # Quick setup script
│   ├── run.sh            # Application runner
│   └── setup_uv.sh       # UV package manager setup
├── tests/                 # Test files
│   ├── test_real_data.py # Real data validation
│   ├── test_fixes.py     # Bug fix verification
│   └── test_final.py     # System integration tests
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── .env.example         # Environment template
```

## Critical Debugging Lessons

### 1. Agent Output Display Fix

**Problem**: AI agents returning content but UI showing placeholders
**Solution**: In `main.py`, properly extract agent content:

```python
def format_agent_result(agent_text):
    # Remove header (## 에이전트명의 분석...)
    # Remove footer (---\n*agent_name...)
    # Extract actual content between headers and footers
```

### 2. Import Path Consistency

**Problem**: ModuleNotFoundError after file reorganization
**Solution**: Always use relative imports from `utils`, not `core`:

```python
from ..utils import get_config  # Correct
# from ..core import get_config  # Wrong (core was removed)
```

### 3. Model Configuration

**Problem**: Invalid model names causing API errors
**Solution**: Use valid OpenAI models:

```python
DEFAULT_MODEL=gpt-4o-mini  # Valid, cost-effective
# DEFAULT_MODEL=gpt-5-nano  # Invalid, doesn't exist
```

### 4. Financial Data Accuracy

**Problem**: Incorrect PER values (showing 39.4 instead of 256.67 for TSLA)
**Solution**: Pass actual stock_data to CompanyAnalystAgent:

```python
# In decision_system.py
agent_results["기업분석가"] = company_agent._run(
    company, market, stock_data=stock_data  # Pass actual data
)
```

## Development Commands

```bash
# Code quality
ruff check .                    # Lint code
ruff check . --fix              # Auto-fix linting issues
black investment_advisor/       # Format code
mypy investment_advisor/        # Type checking

# Testing
python tests/test_real_data.py  # Test Yahoo Finance integration
python tests/test_fixes.py       # Verify bug fixes
python tests/test_final.py       # System integration test

# Cache management
rm -rf .cache/                  # Clear all cache
find .cache -mtime +1 -delete   # Clear old cache
```

## Data Flow Architecture

### Three-Tier Data Fetching System

1. **Primary**: `YahooFetcher` → Real-time market data
2. **Fallback**: `StableFetcher` → Backup data source
3. **Emergency**: `SimpleFetcher` → Hardcoded values

### Parallel Agent Execution

```python
# Agents run concurrently via ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        executor.submit(agent._run, company, market): name
        for name, agent in agents.items()
    }
```

## Common Issues & Solutions

### Yahoo Finance Rate Limiting

```bash
# Enable caching
USE_CACHE=true

# Add delays between requests
import time
time.sleep(1)  # Between API calls
```

### Agent Output Truncation

- Check `format_agent_result()` in main.py
- Verify agent returns complete text
- Remove placeholder text patterns

### Memory/Performance Issues

```bash
# Clear cache
rm -rf .cache/

# Limit parallel workers
max_workers=2  # Reduce from 4 if needed

# Check memory usage
ps aux | grep python
```

## Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=sk-...          # OpenAI API key

# Recommended
DEFAULT_MODEL=gpt-4o-mini       # Cost-effective model
MODEL_TEMPERATURE=0.1           # Low for consistency
MAX_TOKENS=800                  # Sufficient for analysis
USE_CACHE=true                  # Avoid rate limits
CACHE_DURATION_MINUTES=15       # Balance freshness/performance
DEBUG_MODE=false                # Enable for troubleshooting
LOG_LEVEL=INFO                  # DEBUG for detailed logs
```

## Testing Checklist

Before deployment, verify:

1. **Data Accuracy**

   - [ ] TSLA shows PER ~256 (not ~71)
   - [ ] Samsung (005930) shows ~79,700 KRW
   - [ ] Volume data displays correctly

2. **Agent Output**

   - [ ] All 6 agents return complete analysis
   - [ ] No placeholder text in UI
   - [ ] Confidence levels display (높음/보통/낮음)

3. **Performance**
   - [ ] Analysis completes in <45 seconds
   - [ ] Cache hits for repeated queries
   - [ ] No memory leaks after multiple runs

## Key Files Reference

| File                          | Purpose             | Critical Functions                        |
| ----------------------------- | ------------------- | ----------------------------------------- |
| `main.py`                     | UI orchestration    | `format_agent_result()`, `run_analysis()` |
| `analysis/decision_system.py` | Agent coordination  | `analyze()`, data fetching fallback       |
| `agents/company_analyst.py`   | Financial analysis  | Must receive `stock_data` parameter       |
| `data/yahoo_fetcher.py`       | Primary data source | Real-time market data                     |
| `utils/config.py`             | Configuration       | Model settings, API keys                  |

## Performance Metrics

- **Analysis Time**: 30-45 seconds (6 agents parallel)
- **Cache Hit Rate**: >80% for repeated queries
- **Memory Usage**: ~500MB typical, 1GB peak
- **API Costs**: ~$0.02 per analysis (gpt-4o-mini)

## Version History

- **v0.2 Beta (Current)**: Fixed agent output, accurate PER values
- **v0.1**: Initial release with 6 agents

## Important Notes

1. **Always test with real stocks** (TSLA, AAPL, 005930) to verify data accuracy
2. **Monitor API usage** to avoid unexpected costs
3. **Clear cache** if data seems stale (>15 minutes old)
4. **Use debug mode** for troubleshooting agent issues
5. **Check terminal logs** - agents log completion even if UI doesn't show

## Maintenance Tasks

Weekly:

- Clear old cache files
- Review error logs
- Update test data expectations

Monthly:

- Update model configurations if new versions available
- Review API usage and costs
- Update documentation with new issues/solutions
