"""
Custom exceptions for Investment Advisor system

Provides a hierarchy of exceptions for better error handling and debugging.
"""

from typing import Optional, Dict, Any


class InvestmentAdvisorError(Exception):
    """Base exception for all Investment Advisor errors"""
    
    def __init__(self, 
                 message: str, 
                 error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class DataFetchError(InvestmentAdvisorError):
    """Error occurred while fetching data from external sources"""
    
    def __init__(self, 
                 message: str,
                 source: Optional[str] = None,
                 ticker: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="DATA_FETCH_ERROR", **kwargs)
        self.source = source
        self.ticker = ticker
        if source:
            self.details['source'] = source
        if ticker:
            self.details['ticker'] = ticker


class AnalysisError(InvestmentAdvisorError):
    """Error occurred during analysis process"""
    
    def __init__(self,
                 message: str,
                 agent: Optional[str] = None,
                 stage: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="ANALYSIS_ERROR", **kwargs)
        self.agent = agent
        self.stage = stage
        if agent:
            self.details['agent'] = agent
        if stage:
            self.details['stage'] = stage


class ConfigurationError(InvestmentAdvisorError):
    """Configuration related errors"""
    
    def __init__(self,
                 message: str,
                 config_key: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)
        self.config_key = config_key
        if config_key:
            self.details['config_key'] = config_key


class ValidationError(InvestmentAdvisorError):
    """Input validation errors"""
    
    def __init__(self,
                 message: str,
                 field: Optional[str] = None,
                 value: Optional[Any] = None,
                 **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        self.value = value
        if field:
            self.details['field'] = field
        if value is not None:
            self.details['value'] = str(value)


class RateLimitError(DataFetchError):
    """Rate limit exceeded error"""
    
    def __init__(self,
                 message: str = "Rate limit exceeded",
                 retry_after: Optional[int] = None,
                 **kwargs):
        super().__init__(message, error_code="RATE_LIMIT_ERROR", **kwargs)
        self.retry_after = retry_after
        if retry_after:
            self.details['retry_after'] = retry_after


class AuthenticationError(InvestmentAdvisorError):
    """Authentication/API key related errors"""
    
    def __init__(self,
                 message: str = "Authentication failed",
                 service: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)
        self.service = service
        if service:
            self.details['service'] = service