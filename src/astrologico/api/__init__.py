"""
API module for Astrologico.

Provides FastAPI-based REST API for astrological calculations and AI interpretation.
Includes request logging, error handling, performance monitoring, and metrics.
"""

from astrologico.api.app import create_app, app
from astrologico.api.settings import settings
from astrologico.api.models import (
    ChartRequest,
    ChartResponse,
    CompatibilityRequest,
    QuestionRequest,
    LocationInput,
    DateTimeInput
)
from astrologico.api.dependencies import (
    get_calculator,
    get_interpreter,
    reset_dependencies
)
from astrologico.api.utils import (
    validate_coordinates,
    parse_datetime,
    format_chart_response,
    validate_and_parse_location,
    standardize_response
)
from astrologico.api.logging_config import (
    setup_logging,
    get_logger,
    get_log_config
)
from astrologico.api.error_handling import (
    ErrorResponse,
    ErrorHandlingMiddleware,
    HTTPExceptionHandler
)
from astrologico.api.middleware import (
    RequestLoggingMiddleware,
    PerformanceMonitoringMiddleware,
    RequestContextMiddleware
)

__all__ = [
    # Core
    'app',
    'create_app',
    'settings',
    
    # Models
    'ChartRequest',
    'ChartResponse',
    'CompatibilityRequest',
    'QuestionRequest',
    'LocationInput',
    'DateTimeInput',
    
    # Dependencies
    'get_calculator',
    'get_interpreter',
    'reset_dependencies',
    
    # Utilities
    'validate_coordinates',
    'parse_datetime',
    'format_chart_response',
    'validate_and_parse_location',
    'standardize_response',
    
    # Logging
    'setup_logging',
    'get_logger',
    'get_log_config',
    
    # Error Handling
    'ErrorResponse',
    'ErrorHandlingMiddleware',
    'HTTPExceptionHandler',
    
    # Middleware
    'RequestLoggingMiddleware',
    'PerformanceMonitoringMiddleware',
    'RequestContextMiddleware'
]
