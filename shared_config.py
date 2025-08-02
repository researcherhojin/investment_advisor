"""
Shared Configuration

Common configuration shared between Streamlit and FastAPI applications.
This ensures consistency across both platforms during migration.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class MarketConfig:
    """Market-specific configuration."""
    name_ko: str
    name_en: str
    currency: str
    trading_hours: str
    timezone: str


@dataclass
class AgentConfig:
    """AI Agent configuration."""
    name_ko: str
    name_en: str
    color: str
    icon: str
    weight: float = 1.0  # Weight in final decision


@dataclass
class SharedConfig:
    """Shared configuration between Streamlit and FastAPI."""
    
    # Application
    app_name: str = "AI Investment Advisory System"
    version: str = "1.0.0"
    
    # AI Configuration
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = "gpt-4o-mini-2024-07-18"
    openai_temperature: float = 0.1
    
    # Market Configuration
    markets: Dict[str, MarketConfig] = field(default_factory=lambda: {
        "US": MarketConfig(
            name_ko="미국장",
            name_en="US Market",
            currency="USD",
            trading_hours="09:30-16:00 EST",
            timezone="America/New_York"
        ),
        "KR": MarketConfig(
            name_ko="한국장",
            name_en="Korean Market",
            currency="KRW",
            trading_hours="09:00-15:30 KST",
            timezone="Asia/Seoul"
        )
    })
    
    # Agent Configuration
    agents: Dict[str, AgentConfig] = field(default_factory=lambda: {
        "company_analyst": AgentConfig(
            name_ko="기업분석가",
            name_en="Company Analyst",
            color="#1E88E5",
            icon="🏢",
            weight=1.2
        ),
        "industry_expert": AgentConfig(
            name_ko="산업전문가",
            name_en="Industry Expert",
            color="#43A047",
            icon="🏭",
            weight=1.0
        ),
        "macroeconomist": AgentConfig(
            name_ko="거시경제학자",
            name_en="Macroeconomist",
            color="#E53935",
            icon="🌍",
            weight=0.8
        ),
        "technical_analyst": AgentConfig(
            name_ko="기술분석가",
            name_en="Technical Analyst",
            color="#FB8C00",
            icon="📊",
            weight=1.0
        ),
        "risk_manager": AgentConfig(
            name_ko="리스크매니저",
            name_en="Risk Manager",
            color="#8E24AA",
            icon="⚠️",
            weight=1.1
        ),
        "mediator": AgentConfig(
            name_ko="중재자",
            name_en="Mediator",
            color="#00ACC1",
            icon="🤝",
            weight=1.5
        )
    })
    
    # Cache Configuration
    cache_enabled: bool = True
    cache_ttl: int = 900  # 15 minutes
    
    # Analysis Configuration
    default_analysis_period: int = 12  # months
    max_analysis_period: int = 36
    min_confidence_threshold: float = 0.6
    
    # UI Configuration
    theme_colors: Dict[str, str] = field(default_factory=lambda: {
        "primary": "#1E88E5",
        "secondary": "#00ACC1",
        "success": "#43A047",
        "warning": "#FB8C00",
        "danger": "#E53935",
        "dark": "#1E1E1E",
        "light": "#F5F5F5"
    })
    
    # Feature Flags
    use_streamlit_agents: bool = field(
        default_factory=lambda: os.getenv("USE_STREAMLIT_AGENTS", "true").lower() == "true"
    )
    enable_caching: bool = field(
        default_factory=lambda: os.getenv("ENABLE_CACHING", "true").lower() == "true"
    )
    enable_debug_mode: bool = field(
        default_factory=lambda: os.getenv("DEBUG_MODE", "false").lower() == "true"
    )
    
    # Data Sources
    primary_data_source: str = "stable_fetcher"  # "yahoo_finance" or "stable_fetcher"
    fallback_data_sources: list = field(default_factory=lambda: ["alpha_vantage", "finnhub"])
    
    # Stock Data
    popular_stocks: Dict[str, list] = field(default_factory=lambda: {
        "US": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK.B"],
        "KR": ["005930", "000660", "035420", "005380", "051910", "006400", "035720", "003550"]
    })
    
    def get_market_name(self, market: str, language: str = "ko") -> str:
        """Get market name in specified language."""
        if market in self.markets:
            return self.markets[market].name_ko if language == "ko" else self.markets[market].name_en
        return market
    
    def get_agent_info(self, agent_type: str, language: str = "ko") -> Dict[str, Any]:
        """Get agent information in specified language."""
        if agent_type in self.agents:
            agent = self.agents[agent_type]
            return {
                "name": agent.name_ko if language == "ko" else agent.name_en,
                "color": agent.color,
                "icon": agent.icon,
                "weight": agent.weight
            }
        return {"name": agent_type, "color": "#666666", "icon": "🤖", "weight": 1.0}
    
    def get_investment_decision_style(self, decision: str) -> Dict[str, str]:
        """Get styling for investment decision."""
        styles = {
            "BUY": {
                "background": "linear-gradient(135deg, #43A047, #66BB6A)",
                "color": "white",
                "icon": "📈",
                "text_ko": "매수",
                "text_en": "Buy"
            },
            "SELL": {
                "background": "linear-gradient(135deg, #E53935, #EF5350)",
                "color": "white",
                "icon": "📉",
                "text_ko": "매도",
                "text_en": "Sell"
            },
            "HOLD": {
                "background": "linear-gradient(135deg, #FB8C00, #FFA726)",
                "color": "white",
                "icon": "⏸️",
                "text_ko": "보유",
                "text_en": "Hold"
            }
        }
        return styles.get(decision.upper(), styles["HOLD"])
    
    @classmethod
    def load_from_env(cls) -> "SharedConfig":
        """Load configuration from environment variables."""
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "markets": {k: v.__dict__ for k, v in self.markets.items()},
            "agents": {k: v.__dict__ for k, v in self.agents.items()},
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "use_streamlit_agents": self.use_streamlit_agents,
            "primary_data_source": self.primary_data_source
        }


# Global configuration instance
shared_config = SharedConfig.load_from_env()


# Utility functions for backward compatibility
def get_market_mapping() -> Dict[str, str]:
    """Get market name mapping for backward compatibility."""
    return {
        "US": shared_config.markets["US"].name_ko,
        "미국장": "US",
        "KR": shared_config.markets["KR"].name_ko,
        "한국장": "KR"
    }


def get_agent_colors() -> Dict[str, str]:
    """Get agent color mapping."""
    return {k: v.color for k, v in shared_config.agents.items()}


def get_supported_markets() -> list:
    """Get list of supported markets."""
    return list(shared_config.markets.keys())