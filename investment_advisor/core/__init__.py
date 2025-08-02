"""
Core module for Investment Advisor

Contains base classes, exceptions, and utilities.
"""

from .exceptions import (
    InvestmentAdvisorError,
    DataFetchError,
    AnalysisError,
    ConfigurationError,
    ValidationError,
    RateLimitError,
    AuthenticationError
)
from .config import get_settings, Settings
from .mixins import RetryMixin, CacheMixin, LoggingMixin, ValidationMixin
from .types import (
    Market, Decision, Confidence,
    StockInfo, TechnicalIndicators, FundamentalScores,
    RiskMetrics, AnalysisResult
)

__all__ = [
    # Exceptions
    'InvestmentAdvisorError',
    'DataFetchError', 
    'AnalysisError',
    'ConfigurationError',
    'ValidationError',
    'RateLimitError',
    'AuthenticationError',
    # Config
    'get_settings',
    'Settings',
    # Mixins
    'RetryMixin',
    'CacheMixin',
    'LoggingMixin',
    'ValidationMixin',
    # Types
    'Market',
    'Decision',
    'Confidence',
    'StockInfo',
    'TechnicalIndicators',
    'FundamentalScores',
    'RiskMetrics',
    'AnalysisResult',
]