"""
Configuration Management

Centralized configuration management using Pydantic.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    alpha_vantage_key: Optional[str] = Field(None, env="ALPHA_VANTAGE_API_KEY")
    polygon_api_key: Optional[str] = Field(None, env="POLYGON_API_KEY")
    
    # Model Configuration
    default_model: str = Field("gpt-4o-mini-2024-07-18", env="DEFAULT_MODEL")
    temperature: float = Field(0.1, env="MODEL_TEMPERATURE")
    max_tokens: int = Field(4000, env="MODEL_MAX_TOKENS")
    
    # Data Configuration
    cache_enabled: bool = Field(True, env="USE_CACHE")
    cache_ttl: int = Field(900, env="CACHE_TTL")  # 15 minutes default
    
    # Application Configuration
    request_timeout: int = Field(15, env="REQUEST_TIMEOUT")
    max_retries: int = Field(3, env="MAX_RETRIES")
    request_delay: float = Field(1.5, env="REQUEST_DELAY")
    
    # Feature Flags
    use_mock_data_first: bool = Field(True, env="USE_MOCK_DATA_FIRST")
    enable_advanced_features: bool = Field(True, env="ENABLE_ADVANCED_FEATURES")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from environment


# Singleton pattern
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset settings (useful for testing)."""
    global _settings
    _settings = None