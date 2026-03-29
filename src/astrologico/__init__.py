"""
Astrologico - Professional Astrological Calculation Suite.

Provides comprehensive astrological calculations, AI interpretation,
and REST API services for chart analysis and forecasting.

Modules:
    - core: Core calculation engine (calculator, models, serialization)
    - ai: AI-powered interpretation (OpenAI, Anthropic)
    - api: REST API server (FastAPI application and routes)
    - cli: Command-line interface
    - client: HTTP client for API interaction
"""

__version__ = "2.0.0"
__author__ = "Astrologico Team"
__license__ = "MIT"

from astrologico.core import (
    AstrologicalCalculator,
    ChartData,
    PlanetaryPosition,
    AspectType,
    AspectData,
    chart_to_dict,
    planetary_position_to_dict,
    format_chart_output
)
from astrologico.ai import AstrologicalInterpreter
from astrologico.api import app, create_app, settings
from astrologico.cli import main as cli_main
from astrologico.client import AstrologicoAPIClient

__all__ = [
    # Core
    'AstrologicalCalculator',
    'ChartData',
    'PlanetaryPosition',
    'AspectType',
    'AspectData',
    'chart_to_dict',
    'planetary_position_to_dict',
    'format_chart_output',
    # AI
    'AstrologicalInterpreter',
    # API
    'app',
    'create_app',
    'settings',
    # CLI
    'cli_main',
    # Client
    'AstrologicoAPIClient'
]
