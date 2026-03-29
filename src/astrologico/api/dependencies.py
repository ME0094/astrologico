"""
Shared API dependencies.

Provides singleton instances of calculator and interpreter for use across all routes.
This prevents multiple instantiations and ensures consistent configuration across endpoints.
"""

from typing import Optional
from src.astrologico.core import AstrologicalCalculator
from src.astrologico.ai import AstrologicalInterpreter
from src.astrologico.api.settings import settings

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


__all__ = [
    'get_calculator',
    'get_interpreter',
    'reset_dependencies'
]
