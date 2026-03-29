"""
Shared API dependencies.

Provides singleton instances of calculator and interpreter for use across all routes.
This prevents multiple instantiations and ensures consistent configuration across endpoints.
Also provides authentication dependencies for securing API endpoints.
"""

from typing import Optional
from fastapi import HTTPException, Security, Header, Depends
from fastapi.security import APIKeyHeader

from astrologico.core import AstrologicalCalculator
from astrologico.ai import AstrologicalInterpreter
from astrologico.api.settings import settings
from astrologico.api.logging_config import get_logger

logger = get_logger(__name__)

# Singleton instances
_calculator: Optional[AstrologicalCalculator] = None
_interpreter: Optional[AstrologicalInterpreter] = None


def get_calculator() -> AstrologicalCalculator:
    """
    Get or create the AstrologicalCalculator singleton.
    
    Returns:
        Shared AstrologicalCalculator instance
    """
    global _calculator
    if _calculator is None:
        _calculator = AstrologicalCalculator()
    return _calculator


def get_interpreter() -> AstrologicalInterpreter:
    """
    Get or create the AstrologicalInterpreter singleton.
    
    Returns:
        Shared AstrologicalInterpreter instance configured with API settings
    """
    global _interpreter
    if _interpreter is None:
        api_key = settings.openai_api_key or settings.anthropic_api_key
        _interpreter = AstrologicalInterpreter(
            api_provider=settings.ai_provider,
            api_key=api_key
        )
    return _interpreter


def reset_dependencies() -> None:
    """
    Reset singleton instances (useful for testing).
    """
    global _calculator, _interpreter
    _calculator = None
    _interpreter = None


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias=settings.api_key_header)
) -> str:
    """
    Verify API key from request header.
    
    Args:
        x_api_key: API key from request header
        
    Returns:
        The verified API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    # If API key is not required, allow all requests
    if not settings.require_api_key:
        return "public"
    
    # If API key is required but not provided
    if not x_api_key:
        logger.warning("Request missing API key header")
        raise HTTPException(
            status_code=403,
            detail="API key required. Provide in X-API-Key header."
        )
    
    # Verify API key
    if not settings.is_api_key_valid(x_api_key):
        logger.warning(f"Invalid API key attempt from request")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    logger.debug("API key validation successful")
    return x_api_key


async def verify_ai_api_key(
    x_api_key: Optional[str] = Header(None, alias=settings.api_key_header)
) -> str:
    """
    Verify API key for AI endpoints only.
    
    Uses verify_api_key for general validation, but only enforces it if
    require_api_key_for_ai is True.
    
    Args:
        x_api_key: API key from request header
        
    Returns:
        The verified API key or "public" if not required
        
    Raises:
        HTTPException: If AI API key is required but missing/invalid
    """
    # Check if AI endpoints require API key
    if settings.requires_api_key_for_ai():
        return await verify_api_key(x_api_key)
    
    # AI key not required
    return "public"


__all__ = [
    'get_calculator',
    'get_interpreter',
    'reset_dependencies',
    'verify_api_key',
    'verify_ai_api_key',
]
