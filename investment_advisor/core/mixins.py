"""
Mixins for common functionality

Provides reusable components to reduce code duplication.
"""

import time
import random
import logging
from typing import Callable, TypeVar, Optional, Any, Dict
from functools import wraps
import asyncio

from .exceptions import DataFetchError, RateLimitError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryMixin:
    """Mixin for adding retry functionality with exponential backoff"""
    
    # Default configuration
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    
    def with_retry(self, 
                   func: Callable[..., T],
                   *args,
                   max_retries: Optional[int] = None,
                   **kwargs) -> T:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            max_retries: Override default max retries
            *args, **kwargs: Arguments for the function
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        retries = max_retries or self.max_retries
        last_exception = None
        
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                # Special handling for rate limits
                if e.retry_after:
                    delay = min(e.retry_after, self.max_delay)
                else:
                    delay = self._calculate_delay(attempt)
                last_exception = e
            except Exception as e:
                delay = self._calculate_delay(attempt)
                last_exception = e
                
            if attempt < retries - 1:
                logger.warning(
                    f"Attempt {attempt + 1}/{retries} failed: {str(e)}. "
                    f"Retrying in {delay:.1f} seconds..."
                )
                time.sleep(delay)
            else:
                logger.error(f"All {retries} attempts failed.")
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter"""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            # Add random jitter (±25%)
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    async def with_retry_async(self,
                              func: Callable[..., T],
                              *args,
                              max_retries: Optional[int] = None,
                              **kwargs) -> T:
        """Async version of with_retry"""
        retries = max_retries or self.max_retries
        last_exception = None
        
        for attempt in range(retries):
            try:
                return await func(*args, **kwargs)
            except RateLimitError as e:
                if e.retry_after:
                    delay = min(e.retry_after, self.max_delay)
                else:
                    delay = self._calculate_delay(attempt)
                last_exception = e
            except Exception as e:
                delay = self._calculate_delay(attempt)
                last_exception = e
                
            if attempt < retries - 1:
                logger.warning(
                    f"Async attempt {attempt + 1}/{retries} failed: {str(e)}. "
                    f"Retrying in {delay:.1f} seconds..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {retries} async attempts failed.")
        
        raise last_exception


class CacheMixin:
    """Mixin for adding caching functionality"""
    
    _cache: Dict[str, Any] = {}
    cache_ttl: int = 900  # 15 minutes default
    
    def get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                logger.debug(f"Cache expired for key: {key}")
                del self._cache[key]
        return None
    
    def set_cache(self, key: str, value: Any) -> None:
        """Set value in cache with timestamp"""
        self._cache[key] = (value, time.time())
        logger.debug(f"Cached value for key: {key}")
    
    def clear_cache(self, pattern: Optional[str] = None) -> None:
        """Clear cache entries matching pattern or all if pattern is None"""
        if pattern is None:
            self._cache.clear()
            logger.info("Cleared entire cache")
        else:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
            logger.info(f"Cleared {len(keys_to_remove)} cache entries matching '{pattern}'")
    
    def cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return ":".join(key_parts)


class LoggingMixin:
    """Mixin for standardized logging"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for the class"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__module__)
        return self._logger
    
    def log_operation(self, operation: str):
        """Decorator for logging method execution"""
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                self.logger.info(f"Starting {operation}...")
                start_time = time.time()
                
                try:
                    result = func(self, *args, **kwargs)
                    elapsed = time.time() - start_time
                    self.logger.info(f"Completed {operation} in {elapsed:.2f}s")
                    return result
                except Exception as e:
                    elapsed = time.time() - start_time
                    self.logger.error(
                        f"Failed {operation} after {elapsed:.2f}s: {str(e)}"
                    )
                    raise
            
            return wrapper
        return decorator


class ValidationMixin:
    """Mixin for input validation"""
    
    def validate_ticker(self, ticker: str, market: str) -> str:
        """Validate and normalize ticker symbol"""
        from ..utils import InputValidator
        
        validator = InputValidator()
        result = validator.validate_ticker(ticker, market)
        
        if not result['valid']:
            from .exceptions import ValidationError
            raise ValidationError(
                result['message'],
                field='ticker',
                value=ticker
            )
        
        return result['normalized_ticker']
    
    def validate_period(self, period: int) -> int:
        """Validate analysis period"""
        if not isinstance(period, int):
            from .exceptions import ValidationError
            raise ValidationError(
                "Period must be an integer",
                field='period',
                value=period
            )
        
        if period < 1 or period > 60:
            from .exceptions import ValidationError
            raise ValidationError(
                "Period must be between 1 and 60 months",
                field='period',
                value=period
            )
        
        return period