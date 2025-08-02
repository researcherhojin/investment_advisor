"""
Core module for Investment Advisor

Contains base classes, exceptions, and utilities.
"""

from .exceptions import (
    InvestmentAdvisorError,
    DataFetchError,
    AnalysisError,
    ConfigurationError,
    ValidationError
)

__all__ = [
    'InvestmentAdvisorError',
    'DataFetchError', 
    'AnalysisError',
    'ConfigurationError',
    'ValidationError'
]