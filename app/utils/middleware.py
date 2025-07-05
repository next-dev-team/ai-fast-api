import time
import json
from typing import Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from aiolimiter import AsyncLimiter

from ..config import settings
from .logger import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using aiolimiter."""
    
    def __init__(self, app, max_requests: int = None, time_window: int = None):
        super().__init__(app)
        self.max_requests = max_requests or settings.rate_limit_requests
        self.time_window = time_window or settings.rate_limit_window
        self.limiter = AsyncLimiter(self.max_requests, self.time_window)
        self.client_limiters: Dict[str, AsyncLimiter] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Create per-client limiter if not exists
        if client_ip not in self.client_limiters:
            self.client_limiters[client_ip] = AsyncLimiter(
                self.max_requests, 
                self.time_window
            )
        
        # Check rate limit
        limiter = self.client_limiters[client_ip]
        
        if not await limiter.acquire(amount=1):
            logger.warning(f"Rate limit exceeded for client: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "message": "Rate limit exceeded",
                        "type": "rate_limit_error",
                        "code": "rate_limit_exceeded"
                    }
                },
                headers={
                    "Retry-After": str(self.time_window),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Window": str(self.time_window)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Window"] = str(self.time_window)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {self._get_client_ip(request)}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} "
                f"({process_time:.3f}s)"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {str(e)} ({process_time:.3f}s)"
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            # Re-raise HTTP exceptions (they're handled by FastAPI)
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            
            # Return generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": "Internal server error",
                        "type": "server_error",
                        "code": "internal_error"
                    }
                }
            )


def create_error_response(
    message: str, 
    error_type: str = "server_error", 
    code: str = "internal_error",
    status_code: int = 500
) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "type": error_type,
                "code": code
            }
        }
    )