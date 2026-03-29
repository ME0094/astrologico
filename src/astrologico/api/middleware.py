"""
Request/response logging and performance monitoring middleware.

Provides detailed logging of HTTP requests and responses, tracks performance metrics,
includes request correlation IDs for tracing, and monitors endpoint usage.
"""

import logging
import time
import uuid
from typing import Callable, Dict, Any, Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.astrologico.api.settings import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses with performance metrics.
    
    Features:
    - Assigns unique request ID for tracing
    - Logs request method, path, query parameters
    - Measures request processing time
    - Logs response status and size
    - Tracks performance metrics
    - Environment-aware verbose logging
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response with performance metrics.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
        
        Returns:
            HTTP response with metrics
        """
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.scope["request_id"] = request_id
        
        # Extract request information
        method = request.method
        path = request.url.path
        query_string = request.url.query
        client_addr = request.client.host if request.client else "unknown"
        
        # Start timing
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"→ {method} {path}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_string": query_string,
                "client": client_addr,
                "event": "request_start"
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log error and re-raise
            elapsed_time = (time.time() - start_time) * 1000  # milliseconds
            logger.error(
                f"✗ {method} {path} (Failed after {elapsed_time:.2f}ms)",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "elapsed_time_ms": elapsed_time,
                    "error": str(exc),
                    "event": "request_error"
                },
                exc_info=True
            )
            raise
        
        # Calculate metrics
        elapsed_time = (time.time() - start_time) * 1000  # milliseconds
        status_code = response.status_code
        
        # Determine status indicator
        if 200 <= status_code < 300:
            status_indicator = "✓"
            level = logging.INFO
        elif 300 <= status_code < 400:
            status_indicator = "⟳"
            level = logging.INFO
        elif 400 <= status_code < 500:
            status_indicator = "⚠"
            level = logging.WARNING
        else:
            status_indicator = "✗"
            level = logging.ERROR
        
        # Log response
        log_message = (
            f"{status_indicator} {method} {path} - {status_code} "
            f"({elapsed_time:.2f}ms)"
        )
        
        logger.log(
            level,
            log_message,
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "elapsed_time_ms": elapsed_time,
                "client": client_addr,
                "event": "request_complete"
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Add performance metrics in development
        if settings.is_development():
            response.headers["X-Process-Time"] = str(elapsed_time)
        
        return response


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking API performance metrics.
    
    Tracks:
    - Response times by endpoint
    - Error rates by endpoint
    - Request count by method/path
    """
    
    # Class-level metrics storage
    metrics: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Monitor performance for the request.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
        
        Returns:
            HTTP response
        """
        endpoint_key = f"{request.method}:{request.url.path}"
        
        # Initialize metrics for this endpoint if needed
        if endpoint_key not in self.metrics:
            self.metrics[endpoint_key] = {
                "count": 0,
                "errors": 0,
                "total_time": 0.0,
                "max_time": 0.0,
                "min_time": float('inf'),
            }
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            elapsed_time = (time.time() - start_time) * 1000
            
            # Update metrics
            metrics = self.metrics[endpoint_key]
            metrics["count"] += 1
            metrics["total_time"] += elapsed_time
            metrics["max_time"] = max(metrics["max_time"], elapsed_time)
            metrics["min_time"] = min(metrics["min_time"], elapsed_time)
            
            if response.status_code >= 400:
                metrics["errors"] += 1
            
            return response
        
        except Exception:
            elapsed_time = (time.time() - start_time) * 1000
            metrics = self.metrics[endpoint_key]
            metrics["count"] += 1
            metrics["errors"] += 1
            metrics["total_time"] += elapsed_time
            metrics["max_time"] = max(metrics["max_time"], elapsed_time)
            metrics["min_time"] = min(metrics["min_time"], elapsed_time)
            raise
    
    @classmethod
    def get_metrics(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get current performance metrics.
        
        Returns:
            Dictionary with metrics for each endpoint
        """
        metrics_with_averages = {}
        for endpoint, metrics in cls.metrics.items():
            avg_time = (
                metrics["total_time"] / metrics["count"]
                if metrics["count"] > 0
                else 0.0
            )
            metrics_with_averages[endpoint] = {
                **metrics,
                "avg_time": avg_time,
                "error_rate": (
                    metrics["errors"] / metrics["count"]
                    if metrics["count"] > 0
                    else 0.0
                )
            }
        return metrics_with_averages
    
    @classmethod
    def reset_metrics(cls) -> None:
        """Reset all collected metrics."""
        cls.metrics.clear()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware for managing request context.
    
    Stores request-scoped information that can be accessed
    by handlers and other middleware.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add context information to request scope.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
        
        Returns:
            HTTP response
        """
        # Add request metadata to scope
        request.scope["start_time"] = time.time()
        request.scope["request_id"] = request.scope.get(
            "request_id",
            str(uuid.uuid4())
        )
        
        response = await call_next(request)
        return response


__all__ = [
    'RequestLoggingMiddleware',
    'PerformanceMonitoringMiddleware',
    'RequestContextMiddleware'
]
