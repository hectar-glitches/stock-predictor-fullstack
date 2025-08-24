"""Middleware for the FastAPI application."""
import time
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog
from config import settings

logger = structlog.get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ERROR_COUNT = Counter('http_errors_total', 'Total HTTP errors', ['method', 'endpoint', 'error_type'])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring and metrics collection."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Skip metrics for metrics endpoint to avoid infinite loop
        if request.url.path == "/metrics":
            return await call_next(request)
        
        try:
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            REQUEST_DURATION.observe(duration)
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            # Log request
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration,
                client_ip=get_remote_address(request)
            )
            
            return response
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            REQUEST_DURATION.observe(duration)
            ERROR_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                error_type=type(e).__name__
            ).inc()
            
            # Log error
            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration=duration,
                client_ip=get_remote_address(request),
                exc_info=True
            )
            
            raise


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


async def metrics_endpoint():
    """Endpoint for Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
