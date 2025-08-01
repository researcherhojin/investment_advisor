"""
Application Configuration

Centralized configuration management using Pydantic Settings.
Supports environment variables and .env files.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and type safety."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    app_name: str = Field(default="AI Investment Advisory API", description="Application name")
    environment: str = Field(default="development", description="Environment (development, production)")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    allowed_origins: List[str] = Field(default=["http://localhost:3000"], description="CORS allowed origins")
    
    # Database
    database_url: str = Field(..., description="PostgreSQL database URL")
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Database max overflow connections")
    auto_migrate: bool = Field(default=True, description="Auto-run database migrations")
    
    # Redis Cache
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis cache URL")
    cache_ttl: int = Field(default=900, description="Default cache TTL in seconds (15 minutes)")
    
    # AI Services
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini-2024-07-18", description="Default OpenAI model")
    openai_temperature: float = Field(default=0.1, description="OpenAI temperature")
    
    # External APIs
    alpha_vantage_api_key: Optional[str] = Field(default=None, description="Alpha Vantage API key")
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")
    
    # Rate Limiting
    rate_limiting_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(default=60, description="Requests per minute limit")
    
    # Background Tasks
    celery_broker_url: Optional[str] = Field(default=None, description="Celery broker URL")
    celery_result_backend: Optional[str] = Field(default=None, description="Celery result backend")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    
    # Feature Flags
    enable_websockets: bool = Field(default=True, description="Enable WebSocket endpoints")
    enable_background_analysis: bool = Field(default=True, description="Enable background analysis tasks")
    enable_caching: bool = Field(default=True, description="Enable response caching")
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be one of: development, staging, production")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        if v.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        return v.upper()
    
    @validator("openai_temperature")
    def validate_temperature(cls, v: float) -> float:
        """Validate OpenAI temperature."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def database_config(self) -> dict:
        """Get database configuration."""
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
        }
    
    @property
    def openai_config(self) -> dict:
        """Get OpenAI configuration."""
        return {
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "temperature": self.openai_temperature,
        }
    
    class Config:
        """Pydantic model configuration."""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()