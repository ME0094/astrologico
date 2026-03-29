"""
Core astrological calculation module.

Exports the main calculator class, data models, and type definitions
for astrological computations.
"""

from src.astrologico.core.models import (
    ChartData,
    PlanetaryPosition,
    AspectType,
    AspectData
)
from src.astrologico.core.calculator import AstrologicalCalculator
from src.astrologico.core.serialization import (
    chart_to_dict,
    planetary_position_to_dict,
    format_chart_output
)
from src.astrologico.core.types import (
    LocationDict,
    PlanetaryPositionDict,
    AspectDict,
    ChartDict,
    InterpretationDict,
    ChartResponseDict,
    Latitude,
    Longitude,
    Coordinates,
    Degrees,
    MoonPhase,
    AstronomicalUnit,
    AspectName,
    APIProvider,
    PlanetsDict,
    AspectsDict,
    is_chart_dict,
    is_aspect_dict,
    is_planetary_position_dict,
    validate_latitude,
    validate_longitude,
    validate_moon_phase,
    validate_degrees,
    chart_dict_to_response_dict
)

__all__ = [
    # Models
    'AstrologicalCalculator',
    'ChartData',
    'PlanetaryPosition',
    'AspectType',
    'AspectData',
    # Functions
    'chart_to_dict',
    'planetary_position_to_dict',
    'format_chart_output',
    # Types - TypedDict
    'LocationDict',
    'PlanetaryPositionDict',
    'AspectDict',
    'ChartDict',
    'InterpretationDict',
    'ChartResponseDict',
    # Types - Aliases
    'Latitude',
    'Longitude',
    'Coordinates',
    'Degrees',
    'MoonPhase',
    'AstronomicalUnit',
    'AspectName',
    'APIProvider',
    'PlanetsDict',
    'AspectsDict',
    # Validators
    'validate_latitude',
    'validate_longitude',
    'validate_moon_phase',
    'validate_degrees',
    # Type guards
    'is_chart_dict',
    'is_aspect_dict',
    'is_planetary_position_dict',
    # Converters
    'chart_dict_to_response_dict'
]
