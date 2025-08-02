# Configuration Guide

## Overview

This project uses a unified configuration system (`shared_config.py`) to ensure consistency between the Streamlit frontend and FastAPI backend during the migration period.

## Configuration Structure

### 1. Shared Configuration (`shared_config.py`)

Located at the project root, this file contains all common settings:

```python
from shared_config import shared_config

# Access configuration
app_name = shared_config.app_name
markets = shared_config.markets
agents = shared_config.agents
```

### 2. Environment Variables

Create a `.env` file in the project root:

```env
# AI Configuration
OPENAI_API_KEY=your_openai_api_key

# Feature Flags
USE_STREAMLIT_AGENTS=true  # Use legacy agents during migration
ENABLE_CACHING=true
DEBUG_MODE=false

# Data Source
PRIMARY_DATA_SOURCE=stable_fetcher  # or yahoo_finance
```

### 3. Streamlit Configuration

Streamlit apps automatically use `shared_config.py`:

```python
from shared_config import shared_config, get_market_mapping

# Access market names
market_mapping = get_market_mapping()  # {"US": "미국장", "KR": "한국장"}

# Access agent information
agent_info = shared_config.get_agent_info("company_analyst", language="ko")
```

### 4. FastAPI Configuration

FastAPI uses both `shared_config.py` and its own `backend/core/config.py`:

```python
from core.config import get_settings

settings = get_settings()
# Inherits from shared_config for common settings
# Adds API-specific settings (database, redis, etc.)
```

## Key Configuration Items

### Markets

```python
markets = {
    "US": {
        "name_ko": "미국장",
        "name_en": "US Market",
        "currency": "USD",
        "trading_hours": "09:30-16:00 EST",
        "timezone": "America/New_York"
    },
    "KR": {
        "name_ko": "한국장",
        "name_en": "Korean Market",
        "currency": "KRW",
        "trading_hours": "09:00-15:30 KST",
        "timezone": "Asia/Seoul"
    }
}
```

### AI Agents

Each agent has:
- `name_ko`: Korean name
- `name_en`: English name
- `color`: UI color theme
- `icon`: Display icon
- `weight`: Importance in final decision (default 1.0)

```python
agents = {
    "company_analyst": {
        "name_ko": "기업분석가",
        "name_en": "Company Analyst",
        "color": "#1E88E5",
        "icon": "🏢",
        "weight": 1.2
    },
    // ... other agents
}
```

### Theme Colors

Consistent color palette across both platforms:

```python
theme_colors = {
    "primary": "#1E88E5",
    "secondary": "#00ACC1",
    "success": "#43A047",
    "warning": "#FB8C00",
    "danger": "#E53935",
    "dark": "#1E1E1E",
    "light": "#F5F5F5"
}
```

## Migration Strategy

### Phase 1: Shared Configuration (Complete)
- ✅ Create `shared_config.py`
- ✅ Update Streamlit to use shared config
- ✅ Update FastAPI to use shared config

### Phase 2: Gradual Migration
- Use `USE_STREAMLIT_AGENTS=true` to keep using existing agents
- Both platforms read from same configuration
- Consistent behavior during transition

### Phase 3: Full Migration
- Set `USE_STREAMLIT_AGENTS=false` to use native FastAPI agents
- Remove Streamlit dependencies
- Complete API-first architecture

## Usage Examples

### 1. Get Market Information

```python
# Streamlit
from shared_config import shared_config

market_name = shared_config.get_market_name("US", language="ko")  # "미국장"

# FastAPI
market_info = shared_config.markets["US"]
currency = market_info.currency  # "USD"
```

### 2. Get Agent Configuration

```python
# Get agent info
agent_info = shared_config.get_agent_info("technical_analyst")
# Returns: {"name": "기술분석가", "color": "#FB8C00", "icon": "📊", "weight": 1.0}

# Get all agent colors
colors = get_agent_colors()
# Returns: {"company_analyst": "#1E88E5", ...}
```

### 3. Check Feature Flags

```python
# Check if using Streamlit agents
if shared_config.use_streamlit_agents:
    # Use legacy agent system
else:
    # Use new FastAPI agents

# Check if caching is enabled
if shared_config.enable_caching:
    # Use cache
```

### 4. Investment Decision Styling

```python
# Get styling for investment decisions
style = shared_config.get_investment_decision_style("BUY")
# Returns: {
#     "background": "linear-gradient(135deg, #43A047, #66BB6A)",
#     "color": "white",
#     "icon": "📈",
#     "text_ko": "매수",
#     "text_en": "Buy"
# }
```

## Environment-Specific Settings

### Development
```env
ENVIRONMENT=development
DEBUG_MODE=true
USE_STREAMLIT_AGENTS=true
PRIMARY_DATA_SOURCE=stable_fetcher
```

### Production
```env
ENVIRONMENT=production
DEBUG_MODE=false
USE_STREAMLIT_AGENTS=false
PRIMARY_DATA_SOURCE=yahoo_finance
ENABLE_CACHING=true
```

## Troubleshooting

### Configuration Not Loading
1. Check `.env` file exists and is in correct location
2. Verify environment variables are set
3. Check import paths are correct

### Inconsistent Behavior
1. Ensure both Streamlit and FastAPI use same `shared_config.py`
2. Restart both services after configuration changes
3. Clear cache if caching is enabled

### Migration Issues
1. Start with `USE_STREAMLIT_AGENTS=true`
2. Test thoroughly before switching to native agents
3. Monitor logs for configuration-related errors