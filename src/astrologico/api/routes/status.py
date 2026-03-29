"""
Status and health check routes.

Provides API health and status information.
"""

from fastapi import APIRouter
from src.astrologico.api.models import HealthCheckResponse, StatusResponse
from src.astrologico.api.dependencies import get_calculator, get_interpreter
from src.astrologico.api.settings import settings

router = APIRouter(prefix="/api/v1", tags=["status"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Check API health status.
    
    Returns health status of calculator and interpreter components.
    """
    interpreter = get_interpreter()
    
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


@router.get("/")
async def root():
    """
    Get API information.
    
    Returns basic API metadata and documentation link.
    """
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs": "/docs"
    }
