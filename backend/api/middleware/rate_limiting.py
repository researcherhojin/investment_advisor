"""
Rate Limiting Middleware

Implements rate limiting based on client IP addresses.
"""

import time
from typing import Dict, Callable

import structlog
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.clients: Dict[str, Dict[str, any]] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean up old entries
        self._cleanup_old_entries(current_time)
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                requests_per_minute=self.requests_per_minute,
            )
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"},
            )
        
        # Record request
        self._record_request(client_ip, current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining_requests(client_ip, current_time)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client has exceeded rate limit."""
        if client_ip not in self.clients:
            return False
        
        client_data = self.clients[client_ip]
        requests_in_window = [
            req_time for req_time in client_data["requests"]
            if current_time - req_time < 60  # 1 minute window
        ]
        
        return len(requests_in_window) >= self.requests_per_minute
    
    def _record_request(self, client_ip: str, current_time: float) -> None:
        """Record a request for the client."""
        if client_ip not in self.clients:
            self.clients[client_ip] = {"requests": []}
        
        self.clients[client_ip]["requests"].append(current_time)
    
    def _get_remaining_requests(self, client_ip: str, current_time: float) -> int:
        """Get remaining requests for the client."""
        if client_ip not in self.clients:
            return self.requests_per_minute
        
        client_data = self.clients[client_ip]
        requests_in_window = [
            req_time for req_time in client_data["requests"]
            if current_time - req_time < 60
        ]
        
        return max(0, self.requests_per_minute - len(requests_in_window))
    
    def _cleanup_old_entries(self, current_time: float) -> None:
        """Clean up old request entries."""
        for client_ip in list(self.clients.keys()):
            client_data = self.clients[client_ip]
            client_data["requests"] = [
                req_time for req_time in client_data["requests"]
                if current_time - req_time < 60
            ]
            
            # Remove client if no recent requests
            if not client_data["requests"]:
                del self.clients[client_ip]