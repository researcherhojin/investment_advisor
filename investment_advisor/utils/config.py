"""
Configuration Management

Handles application configuration from environment variables and config files.
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Application configuration manager."""

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # API Keys
        self.openai_api_key = self._get_env_var("OPENAI_API_KEY", required=True)
        self.alpha_vantage_api_key = self._get_env_var("ALPHA_VANTAGE_API_KEY", required=False)

        # LangChain settings - Disable if no valid API key
        langchain_api_key = self._get_env_var("LANGCHAIN_API_KEY", required=False)
        if langchain_api_key and langchain_api_key != "your_langchain_api_key_here":
            self.langchain_tracing = self._get_env_var("LANGCHAIN_TRACING_V2", default="false").lower() == "true"
            self.langchain_endpoint = self._get_env_var("LANGCHAIN_ENDPOINT", required=False)
            self.langchain_api_key = langchain_api_key
        else:
            # Disable LangChain tracing if no valid API key
            self.langchain_tracing = False
            self.langchain_endpoint = None
            self.langchain_api_key = None

        # Model settings - Optimized for cost-effectiveness
        # GPT-4o-mini: Best cost-performance for investment analysis
        self.default_model = self._get_env_var("DEFAULT_MODEL", default="gpt-4o-mini")
        self.model_temperature = float(self._get_env_var("MODEL_TEMPERATURE", default="0.1"))
        self.max_tokens = int(self._get_env_var("MAX_TOKENS", default="800"))  # Optimized for nano model

        # Cache settings
        self.use_cache = self._get_env_var("USE_CACHE", default="true").lower() == "true"
        self.cache_duration_minutes = int(self._get_env_var("CACHE_DURATION_MINUTES", default="15"))
        self.cache_directory = self._get_env_var("CACHE_DIRECTORY", default=".cache")

        # Application settings
        self.app_title = self._get_env_var("APP_TITLE", default="AI 투자 자문 서비스")
        self.page_layout = self._get_env_var("PAGE_LAYOUT", default="wide")
        self.debug_mode = self._get_env_var("DEBUG_MODE", default="false").lower() == "true"

        # Market settings
        self.default_market = self._get_env_var("DEFAULT_MARKET", default="미국장")
        self.default_analysis_period = int(self._get_env_var("DEFAULT_ANALYSIS_PERIOD", default="12"))

        # Data fetching settings
        self.request_timeout = int(self._get_env_var("REQUEST_TIMEOUT", default="15"))
        self.max_retries = int(self._get_env_var("MAX_RETRIES", default="3"))
        self.retry_delay = float(self._get_env_var("RETRY_DELAY", default="1.0"))

        # Logging settings
        self.log_level = self._get_env_var("LOG_LEVEL", default="INFO").upper()
        self.log_file = self._get_env_var("LOG_FILE", required=False)

        # Security settings
        self.rate_limit_enabled = self._get_env_var("RATE_LIMIT_ENABLED", default="false").lower() == "true"
        self.max_requests_per_minute = int(self._get_env_var("MAX_REQUESTS_PER_MINUTE", default="60"))

        # Feature flags
        self.enable_recommendations = self._get_env_var("ENABLE_RECOMMENDATIONS", default="true").lower() == "true"
        self.enable_sector_analysis = self._get_env_var("ENABLE_SECTOR_ANALYSIS", default="true").lower() == "true"
        self.enable_backtesting = self._get_env_var("ENABLE_BACKTESTING", default="false").lower() == "true"

        # Set up LangChain environment
        self._setup_langchain_env()

        logger.info("Configuration loaded successfully")

    def _get_env_var(self, var_name: str, default: Optional[str] = None, required: bool = False) -> str:
        """
        Get environment variable.

        Args:
            var_name: Environment variable name
            default: Default value if not found
            required: Whether the variable is required

        Returns:
            Environment variable value

        Raises:
            ValueError: If required variable is not found
        """
        # Get from environment variable
        value = os.getenv(var_name)

        # Use default if None
        if value is None:
            if required:
                # For OpenAI API key, provide more helpful error message
                if var_name == "OPENAI_API_KEY":
                    st.error(f"""
                    🔑 OpenAI API 키가 필요합니다!

                    다음 중 하나의 방법으로 설정해주세요:
                    1. `.env` 파일에 추가: `OPENAI_API_KEY=your_key_here`
                    2. 환경 변수로 설정: `export OPENAI_API_KEY=your_key_here`

                    API 키는 https://platform.openai.com/api-keys 에서 생성할 수 있습니다.
                    """)
                    st.stop()
                raise ValueError(f"Required environment variable {var_name} not found")
            value = default

        return value

    def _setup_langchain_env(self):
        """Set up LangChain environment variables."""
        if self.langchain_tracing and self.langchain_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"

            if self.langchain_endpoint:
                os.environ["LANGCHAIN_ENDPOINT"] = self.langchain_endpoint

            if self.langchain_api_key:
                os.environ["LANGCHAIN_API_KEY"] = self.langchain_api_key
        else:
            # Disable LangChain tracing
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
            if "LANGCHAIN_API_KEY" in os.environ:
                del os.environ["LANGCHAIN_API_KEY"]

    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return {
            "model_name": self.default_model,
            "temperature": self.model_temperature,
            "max_tokens": self.max_tokens,
            "openai_api_key": self.openai_api_key,
        }

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        return {
            "use_cache": self.use_cache,
            "cache_duration_minutes": self.cache_duration_minutes,
            "cache_directory": self.cache_directory,
        }

    def get_data_fetcher_config(self) -> Dict[str, Any]:
        """Get data fetcher configuration."""
        return {
            "request_timeout": self.request_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "alpha_vantage_api_key": self.alpha_vantage_api_key,
        }

    def get_streamlit_config(self) -> Dict[str, Any]:
        """Get Streamlit configuration."""
        return {
            "page_title": self.app_title,
            "layout": self.page_layout,
            "initial_sidebar_state": "expanded",
        }

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug_mode or self._get_env_var("ENVIRONMENT", default="production") == "development"

    def validate_config(self) -> bool:
        """
        Validate configuration.

        Returns:
            True if configuration is valid
        """
        try:
            # Check required API keys
            if not self.openai_api_key:
                logger.error("OpenAI API key is required")
                return False

            # Validate numeric values
            if self.model_temperature < 0 or self.model_temperature > 2:
                logger.error("Model temperature must be between 0 and 2")
                return False

            if self.cache_duration_minutes < 1:
                logger.error("Cache duration must be at least 1 minute")
                return False

            # Create cache directory if it doesn't exist
            Path(self.cache_directory).mkdir(exist_ok=True)

            logger.info("Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def get_feature_flags(self) -> Dict[str, bool]:
        """Get all feature flags."""
        return {
            "recommendations": self.enable_recommendations,
            "sector_analysis": self.enable_sector_analysis,
            "backtesting": self.enable_backtesting,
            "rate_limiting": self.rate_limit_enabled,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            "model": self.default_model,
            "temperature": self.model_temperature,
            "use_cache": self.use_cache,
            "cache_duration": self.cache_duration_minutes,
            "app_title": self.app_title,
            "debug_mode": self.debug_mode,
            "default_market": self.default_market,
            "analysis_period": self.default_analysis_period,
            "feature_flags": self.get_feature_flags(),
        }


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance (singleton pattern).

    Returns:
        Configuration instance
    """
    global _config
    if _config is None:
        _config = Config()
        if not _config.validate_config():
            raise RuntimeError("Configuration validation failed")
    return _config


def reload_config() -> Config:
    """
    Reload configuration (useful for tests or configuration changes).

    Returns:
        New configuration instance
    """
    global _config
    _config = None
    return get_config()
