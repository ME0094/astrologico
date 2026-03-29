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
from src.astrologico.api.dependencies import (
    get_calculator,
    get_interpreter,
    reset_dependencies
)
from src.astrologico.api.utils import (
    validate_coordinates,
    parse_datetime,
    format_chart_response,
    validate_and_parse_location,
    standardize_response
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
    'DateTimeInput',
    'get_calculator',
    'get_interpreter',
    'reset_dependencies',
    'validate_coordinates',
    'parse_datetime',
    'format_chart_response',
    'validate_and_parse_location',
    'standardize_response'
]
