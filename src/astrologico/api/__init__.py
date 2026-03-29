"""
API module for Astrologico.

Provides FastAPI-based REST API for astrological calculations and AI interpretation.
"""

from src.astrologico.api.app import create_app, app
from src.astrologico.api.settings import settings
from src.astrologico.api.models import (
    ChartRequest,
    ChartResponse,
    CompatibilityRequest,
    QuestionRequest,
    LocationInput,
    DateTimeInput
)

__all__ = [
    'app',
    'create_app',
    'settings',
    'ChartRequest',
    'ChartResponse',
    'CompatibilityRequest',
    'QuestionRequest',
    'LocationInput',
    'DateTimeInput'
]
