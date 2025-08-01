# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered investment advisory system for analyzing US and Korean stocks using multiple specialized AI agents (Company Analyst, Industry Expert, Macroeconomist, Technical Analyst, Risk Manager).

## Common Development Commands

### Setup and Run
```bash
# Create conda environment
conda create -n stock python=3.12
conda activate stock

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run investment_advisor.py
```

### Environment Variables
Required in `.env` file:
- `OPENAI_API_KEY` - OpenAI API access
- `ALPHA_VANTAGE_API_KEY` - Economic data (optional but recommended)

## Architecture

### Single-File Application Structure
The entire application is in `investment_advisor.py` (~2000+ lines) with these key components:

1. **AI Agent Classes** (lines ~100-800):
   - `CompanyAnalystAgent` - Financial metrics analysis
   - `IndustryExpertAgent` - Sector comparison
   - `MacroeconomistAgent` - Economic indicators
   - `TechnicalAnalystAgent` - Chart patterns & indicators
   - `RiskManagerAgent` - Risk assessment
   - `MediatorAgent` - Synthesizes all insights

2. **Main System** (lines ~800-1200):
   - `InvestmentDecisionSystem` - Orchestrates agent workflow
   - Multi-step analysis process with parallel execution

3. **Streamlit UI** (lines ~1200+):
   - Sidebar for market/ticker selection
   - Interactive Plotly charts
   - Tabbed results display

### Data Flow
1. User selects market (US/Korea) and ticker
2. System fetches data from market-specific sources:
   - US: yfinance
   - Korea: FinanceDataReader, pykrx
3. Each agent analyzes in parallel
4. Mediator synthesizes final recommendation
5. Results displayed with interactive visualizations

## Key Technical Details

### Market-Specific Handling
- Korean tickers: Add ".KS" suffix for KOSPI, ".KQ" for KOSDAQ
- Economic indicators vary by market (Fed rates vs BOK rates)
- Different trading hours and holidays

### LangChain Integration
- Uses `ChatOpenAI` with GPT-4 model
- Structured output with Pydantic models
- Parallel agent execution with `chain.batch()`

### Technical Indicators
- Moving averages (5, 20, 60, 120 days)
- MACD, RSI, Bollinger Bands
- 52-week high/low tracking
- Beta calculation against market index

### Error Handling
- API rate limiting with retries
- Fallback data sources
- Graceful degradation if agents fail

## Testing and Development

### Manual Testing Approach
```bash
# Test with US stock
streamlit run investment_advisor.py
# Select: Market=미국, Ticker=AAPL

# Test with Korean stock  
streamlit run investment_advisor.py
# Select: Market=한국, Ticker=005930 (Samsung)
```

### Common Issues
- API rate limits: Add delays between requests
- Missing data: Check market holidays/trading hours
- Memory usage: Monitor with large date ranges

### Code Style
- Korean comments for UI strings
- English for technical documentation
- Type hints for agent responses
- Pydantic models for structured outputs