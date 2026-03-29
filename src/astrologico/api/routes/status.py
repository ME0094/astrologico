"""
Status and health check routes.

Provides API health and status information, including metrics and logging details.
"""

from typing import Dict, Any
from fastapi import APIRouter
from src.astrologico.api.models import HealthCheckResponse, StatusResponse
from src.astrologico.api.dependencies import get_calculator, get_interpreter
from src.astrologico.api.settings import settings
from src.astrologico.api.middleware import PerformanceMonitoringMiddleware
from src.astrologico.api.logging_config import get_logger

router = APIRouter(prefix="/api/v1", tags=["status"])
logger = get_logger(__name__)


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Check API health status.
    
    Returns health status of calculator and interpreter components.
    """
    interpreter = get_interpreter()
    
    logger.info("Health check performed")
    
    return {
        "status": "healthy",
        "calculator": "ready",
        "interpreter": "ready" if interpreter.client else "no_api_key"
    }


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get detailed API and interpreter status.
    
    Returns:
    - API version
    - Component status
    - AI provider information
    - Available endpoints
    """
    interpreter = get_interpreter()
    
    logger.info("Status check performed")
    
    return {
        "api_version": settings.api_version,
        "calculator_status": "operational",
        "interpreter_status": "operational" if interpreter.client else "no_api_key",
        "interpreter_provider": interpreter.api_provider,
        "ai_features_enabled": bool(interpreter.client),
        "endpoints": {
            "chart": "/api/v1/chart/generate",
            "quick_chart": "/api/v1/chart/quick",
            "planets": "/api/v1/planets",
            "aspects": "/api/v1/aspects",
            "moon": "/api/v1/moon",
            "compatibility": "/api/v1/analysis/compatibility",
            "transits": "/api/v1/analysis/transits",
            "ask": "/api/v1/ask",
            "documentation": "/docs"
        }
    }


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get API performance metrics.
    
    Returns performance statistics for all endpoints:
    - Request count
    - Response times (min, max, average)
    - Error counts and rates
    
    Note:
        Only available if PerformanceMonitoringMiddleware is enabled.
    """
    metrics = PerformanceMonitoringMiddleware.get_metrics()
    
    # Add summary metrics
    total_requests = sum(m["count"] for m in metrics.values())
    total_errors = sum(m["errors"] for m in metrics.values())
    
    logger.info(f"Metrics retrieved: {total_requests} total requests, {total_errors} errors")
    
    return {
        "summary": {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": (
                total_errors / total_requests
                if total_requests > 0
                else 0.0
            ),
            "endpoints": len(metrics)
        },
        "endpoints": metrics
    }


@router.delete("/metrics")
async def reset_metrics() -> Dict[str, str]:
    """
    Reset performance metrics.
    
    Clears all collected performance data.
    Useful for clearing old metrics during testing or analysis.
    
    Returns:
        Confirmation message
    """
    PerformanceMonitoringMiddleware.reset_metrics()
    logger.info("Performance metrics reset")
    
    return {"message": "Metrics reset successfully"}


@router.get("/")
async def root():
    """
    Get API information.
    
    Returns basic API metadata and documentation link.
    """
    logger.debug("Root endpoint accessed")
    
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs": "/docs"
    }
