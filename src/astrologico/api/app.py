"""
FastAPI application factory and configuration.

Creates and configures the main API application with CORS, middleware, and routers.
Includes logging, error handling, and performance monitoring middleware.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from astrologico.api.settings import settings
from astrologico.api.logging_config import setup_logging, get_logger
from astrologico.api.error_handling import ErrorHandlingMiddleware
from astrologico.api.middleware import (
    RequestLoggingMiddleware,
    PerformanceMonitoringMiddleware,
    RequestContextMiddleware,
    RateLimitingMiddleware
)
from astrologico.api.routes import chart, planets, aspects, moon, ask, status

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Includes:
    - CORS middleware for cross-origin requests
    - Error handling middleware for exceptions
    - Request logging with correlation IDs
    - Performance monitoring
    - Request context management
    - All route routers
    
    Returns:
        Configured FastAPI application instance
    """
    # Setup logging
    setup_logging()
    logger.info(
        f"Creating Astrologico API app (environment: {settings.environment})"
    )
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add middleware in order (last added is first executed)
    # Order: RequestContext → RequestLogging → PerformanceMonitoring → RateLimiting → CORS → ErrorHandling
    
    # Error handling middleware (outermost, catches all exceptions)
    app.add_middleware(ErrorHandlingMiddleware)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=settings.allow_credentials,
        allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Rate limiting middleware (if enabled)
    if settings.enable_rate_limiting:
        app.add_middleware(
            RateLimitingMiddleware,
            requests_per_period=settings.rate_limit_requests,
            period_seconds=settings.rate_limit_period
        )
        logger.info(
            f"Rate limiting enabled: {settings.rate_limit_requests} "
            f"requests per {settings.rate_limit_period}s"
        )
    
    # Performance monitoring middleware
    app.add_middleware(PerformanceMonitoringMiddleware)
    
    # Request logging middleware with correlation IDs
    app.add_middleware(RequestLoggingMiddleware)
    
    # Request context middleware (innermost, closest to handlers)
    app.add_middleware(RequestContextMiddleware)
    
    logger.info("Middleware stack configured")
    
    # Include routers
    app.include_router(status.router)
    app.include_router(chart.router)
    app.include_router(planets.router)
    app.include_router(aspects.router)
    app.include_router(moon.router)
    app.include_router(ask.router)
    
    logger.info("All routers registered")
    logger.info(f"API ready on {settings.api_host}:{settings.api_port}")
    
    return app


# Create the application instance
import sys
if 'pytest' not in sys.modules:
    app = create_app()
else:
    app = None


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level=settings.log_level
    )
