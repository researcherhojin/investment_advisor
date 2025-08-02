"""
Redis Cache Manager

Handles Redis connections and caching operations.
"""

import asyncio
import json
from typing import Any, Optional, Union
from datetime import timedelta

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
import structlog

from backend.core.config import get_settings

logger = structlog.get_logger(__name__)


class CacheManager:
    """Manages Redis cache connections and operations."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pool: Optional[ConnectionPool] = None
        self.settings = get_settings()
        self._lock = asyncio.Lock()
    
    async def connect(self) -> None:
        """Initialize Redis connection."""
        async with self._lock:
            if self.redis_client is not None:
                return
            
            try:
                # Create connection pool
                self.pool = redis.ConnectionPool.from_url(
                    self.settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=50,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )
                
                # Create Redis client
                self.redis_client = redis.Redis(connection_pool=self.pool)
                
                # Test connection
                await self.redis_client.ping()
                
                logger.info("Redis connection established successfully")
                
            except Exception as e:
                logger.error("Failed to connect to Redis", error=str(e))
                # Don't raise - cache is optional
                self.redis_client = None
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        async with self._lock:
            if self.redis_client is None:
                return
            
            try:
                await self.redis_client.close()
                if self.pool:
                    await self.pool.disconnect()
                self.redis_client = None
                self.pool = None
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error("Error closing Redis connection", error=str(e))
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.redis_client is None:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        if self.redis_client is None:
            return False
        
        try:
            # Serialize to JSON if needed
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            
            # Convert timedelta to seconds
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            # Set with or without TTL
            if ttl:
                await self.redis_client.setex(key, ttl, value)
            else:
                await self.redis_client.set(key, value)
            
            return True
            
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if self.redis_client is None:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if self.redis_client is None:
            return False
        
        try:
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.error("Cache exists error", key=key, error=str(e))
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if self.redis_client is None:
            return 0
        
        try:
            count = 0
            async for key in self.redis_client.scan_iter(match=pattern):
                await self.redis_client.delete(key)
                count += 1
            return count
        except Exception as e:
            logger.error("Cache clear pattern error", pattern=pattern, error=str(e))
            return 0
    
    async def health_check(self) -> bool:
        """Check if Redis is healthy."""
        if self.redis_client is None:
            return False
        
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False
    
    def create_key(self, prefix: str, *parts: str) -> str:
        """Create a cache key with prefix."""
        return f"{prefix}:{':'.join(str(p) for p in parts)}"


# Singleton instance
cache_manager = CacheManager()


# Cache decorators
def cache_key_builder(prefix: str):
    """Build cache key from function arguments."""
    def key_builder(*args, **kwargs):
        # Skip 'self' for methods
        key_parts = []
        for arg in args[1:] if args and hasattr(args[0], '__self__') else args:
            if hasattr(arg, 'id'):
                key_parts.append(str(arg.id))
            else:
                key_parts.append(str(arg))
        
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        
        return cache_manager.create_key(prefix, *key_parts)
    
    return key_builder


def cached(
    prefix: str,
    ttl: Union[int, timedelta] = 300,
    key_builder=None
):
    """Decorator for caching function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_key_builder(prefix)(*args, **kwargs)
            
            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug("Cache hit", key=cache_key)
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_manager.set(cache_key, result, ttl)
            logger.debug("Cache miss - stored", key=cache_key)
            
            return result
        
        return wrapper
    return decorator