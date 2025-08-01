"""
Advanced Caching System

Intelligent caching with LRU eviction, TTL expiration, and performance monitoring.
"""

import logging
import time
import hashlib
import pickle
import threading
from typing import Any, Dict, Optional, Callable, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from collections import OrderedDict
import json

logger = logging.getLogger(__name__)


class CacheStats:
    """Cache performance statistics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.total_requests = 0
        self.start_time = time.time()
        
    def hit(self):
        """Record cache hit."""
        self.hits += 1
        self.total_requests += 1
        
    def miss(self):
        """Record cache miss."""
        self.misses += 1
        self.total_requests += 1
        
    def evict(self):
        """Record cache eviction."""
        self.evictions += 1
        
    def expire(self):
        """Record cache expiration."""
        self.expirations += 1
        
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        return (self.hits / self.total_requests * 100) if self.total_requests > 0 else 0
        
    @property
    def uptime_seconds(self) -> float:
        """Get cache uptime in seconds."""
        return time.time() - self.start_time
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'expirations': self.expirations,
            'total_requests': self.total_requests,
            'hit_rate': round(self.hit_rate, 2),
            'uptime_seconds': round(self.uptime_seconds, 2),
        }


class CacheEntry:
    """Cache entry with metadata."""
    
    def __init__(self, value: Any, ttl: Optional[float] = None):
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.access_count = 0
        self.ttl = ttl
        self.expires_at = self.created_at + ttl if ttl else None
        
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
        
    def access(self) -> Any:
        """Access the cached value and update metadata."""
        self.last_accessed = time.time()
        self.access_count += 1
        return self.value
        
    @property
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return time.time() - self.created_at
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry metadata to dictionary."""
        return {
            'created_at': self.created_at,
            'last_accessed': self.last_accessed,
            'access_count': self.access_count,
            'age_seconds': round(self.age_seconds, 2),
            'is_expired': self.is_expired(),
            'expires_at': self.expires_at,
        }


class AdvancedCache:
    """
    Advanced caching system with LRU eviction, TTL expiration, and performance monitoring.
    
    Features:
    - LRU (Least Recently Used) eviction policy
    - TTL (Time To Live) expiration
    - Thread-safe operations
    - Performance statistics
    - Memory usage monitoring
    - Configurable size limits
    - Key prefix support
    - Bulk operations
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: Optional[float] = 3600,  # 1 hour
        cleanup_interval: float = 300,  # 5 minutes
        enable_stats: bool = True,
        key_prefix: str = ""
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self.enable_stats = enable_stats
        self.key_prefix = key_prefix
        
        # Thread-safe cache storage
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Statistics
        self.stats = CacheStats() if enable_stats else None
        
        # Background cleanup
        self._cleanup_timer: Optional[threading.Timer] = None
        self._start_cleanup_timer()
        
        logger.info(f"AdvancedCache initialized: max_size={max_size}, default_ttl={default_ttl}s")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        full_key = self._make_key(key)
        
        with self._lock:
            if full_key not in self._cache:
                if self.stats:
                    self.stats.miss()
                return default
            
            entry = self._cache[full_key]
            
            # Check expiration
            if entry.is_expired():
                del self._cache[full_key]
                if self.stats:
                    self.stats.miss()
                    self.stats.expire()
                return default
            
            # Move to end for LRU
            self._cache.move_to_end(full_key)
            
            if self.stats:
                self.stats.hit()
            
            return entry.access()
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        replace: bool = True
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
            replace: Whether to replace existing key
            
        Returns:
            True if set successfully
        """
        full_key = self._make_key(key)
        actual_ttl = ttl if ttl is not None else self.default_ttl
        
        with self._lock:
            # Check if key exists and replace is False
            if not replace and full_key in self._cache:
                return False
            
            # Create cache entry
            entry = CacheEntry(value, actual_ttl)
            
            # Add to cache
            self._cache[full_key] = entry
            self._cache.move_to_end(full_key)
            
            # Evict if necessary
            self._evict_if_needed()
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted
        """
        full_key = self._make_key(key)
        
        with self._lock:
            if full_key in self._cache:
                del self._cache[full_key]
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        full_key = self._make_key(key)
        
        with self._lock:
            if full_key not in self._cache:
                return False
                
            entry = self._cache[full_key]
            if entry.is_expired():
                del self._cache[full_key]
                if self.stats:
                    self.stats.expire()
                return False
                
            return True
    
    def clear(self) -> int:
        """Clear all cache entries. Returns number of entries cleared."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[float] = None
    ) -> Any:
        """
        Get value from cache or set it using factory function.
        
        Args:
            key: Cache key
            factory: Function to generate value if not cached
            ttl: Time to live in seconds
            
        Returns:
            Cached or generated value
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # Generate value
        try:
            value = factory()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            logger.error(f"Factory function failed for key '{key}': {e}")
            raise
    
    def get_many(self, keys: list) -> Dict[str, Any]:
        """Get multiple keys at once."""
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def set_many(self, mapping: Dict[str, Any], ttl: Optional[float] = None) -> int:
        """Set multiple key-value pairs. Returns number of keys set."""
        count = 0
        for key, value in mapping.items():
            if self.set(key, value, ttl):
                count += 1
        return count
    
    def keys(self, pattern: Optional[str] = None) -> list:
        """Get all cache keys, optionally filtered by pattern."""
        with self._lock:
            keys = list(self._cache.keys())
            
            if pattern:
                import fnmatch
                keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]
            
            # Remove prefix if present
            if self.key_prefix:
                prefix_len = len(self.key_prefix) + 1  # +1 for separator
                keys = [k[prefix_len:] if k.startswith(self.key_prefix + ":") else k for k in keys]
            
            return keys
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns number of entries removed."""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                if self.stats:
                    self.stats.expire()
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """Get cache statistics."""
        if not self.stats:
            return None
        
        with self._lock:
            stats_dict = self.stats.to_dict()
            stats_dict.update({
                'current_size': len(self._cache),
                'max_size': self.max_size,
                'utilization': round(len(self._cache) / self.max_size * 100, 1),
            })
            return stats_dict
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a cache entry."""
        full_key = self._make_key(key)
        
        with self._lock:
            if full_key not in self._cache:
                return None
            
            entry = self._cache[full_key]
            return entry.to_dict()
    
    def _make_key(self, key: str) -> str:
        """Create full cache key with prefix."""
        if self.key_prefix:
            return f"{self.key_prefix}:{key}"
        return key
    
    def _evict_if_needed(self):
        """Evict least recently used entries if cache is full."""
        while len(self._cache) > self.max_size:
            # Remove least recently used (first item in OrderedDict)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            if self.stats:
                self.stats.evict()
            logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def _start_cleanup_timer(self):
        """Start background cleanup timer."""
        if self.cleanup_interval <= 0:
            return
        
        def cleanup():
            try:
                self.cleanup_expired()
            except Exception as e:
                logger.error(f"Cache cleanup failed: {e}")
            finally:
                # Schedule next cleanup
                self._start_cleanup_timer()
        
        self._cleanup_timer = threading.Timer(self.cleanup_interval, cleanup)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def shutdown(self):
        """Shutdown cache and cleanup resources."""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        
        with self._lock:
            self._cache.clear()
        
        logger.info("AdvancedCache shutdown complete")
    
    def __len__(self) -> int:
        """Get cache size."""
        return self.size()
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self.exists(key)
    
    def __getitem__(self, key: str) -> Any:
        """Get item from cache (raises KeyError if not found)."""
        value = self.get(key)
        if value is None:
            raise KeyError(f"Cache key not found: {key}")
        return value
    
    def __setitem__(self, key: str, value: Any):
        """Set item in cache."""
        self.set(key, value)
    
    def __delitem__(self, key: str):
        """Delete item from cache."""
        if not self.delete(key):
            raise KeyError(f"Cache key not found: {key}")


class SmartCacheDecorator:
    """Decorator for intelligent function caching."""
    
    def __init__(
        self,
        cache: Optional[AdvancedCache] = None,
        ttl: Optional[float] = None,
        key_func: Optional[Callable] = None,
        ignore_kwargs: Optional[list] = None
    ):
        self.cache = cache or AdvancedCache()
        self.ttl = ttl
        self.key_func = key_func
        self.ignore_kwargs = ignore_kwargs or []
    
    def __call__(self, func: Callable) -> Callable:
        """Decorate function with caching."""
        def wrapper(*args, **kwargs):
            # Generate cache key
            if self.key_func:
                cache_key = self.key_func(*args, **kwargs)
            else:
                # Filter out ignored kwargs
                filtered_kwargs = {
                    k: v for k, v in kwargs.items() if k not in self.ignore_kwargs
                }
                
                # Create cache key from function name and arguments
                key_data = {
                    'func': func.__name__,
                    'args': args,
                    'kwargs': filtered_kwargs
                }
                cache_key = hashlib.md5(str(key_data).encode()).hexdigest()
            
            # Try to get from cache
            result = self.cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            self.cache.set(cache_key, result, self.ttl)
            
            return result
        
        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.cache = self.cache
        wrapper.cache_clear = lambda: self.cache.clear()
        
        return wrapper


# Global cache instance
_global_cache: Optional[AdvancedCache] = None


def get_global_cache() -> AdvancedCache:
    """Get or create global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = AdvancedCache(
            max_size=500,
            default_ttl=1800,  # 30 minutes
            key_prefix="investment_advisor"
        )
    return _global_cache


def smart_cache(
    ttl: Optional[float] = None,
    key_func: Optional[Callable] = None,
    ignore_kwargs: Optional[list] = None
):
    """
    Decorator for intelligent function caching using global cache.
    
    Args:
        ttl: Time to live in seconds
        key_func: Custom function to generate cache key
        ignore_kwargs: List of kwargs to ignore in cache key
    
    Example:
        @smart_cache(ttl=600)
        def expensive_function(param1, param2):
            # expensive computation
            return result
    """
    return SmartCacheDecorator(
        cache=get_global_cache(),
        ttl=ttl,
        key_func=key_func,
        ignore_kwargs=ignore_kwargs
    )