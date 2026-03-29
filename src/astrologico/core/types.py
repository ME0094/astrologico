"""
Type definitions and schemas for Astrologico.

Provides TypedDict definitions, type aliases, and comprehensive type hints
for internal data structures and API contracts.

This module ensures type consistency across core, AI, and API components
without requiring Pydantic validation for internal operations.
"""

from typing import TypedDict, Dict, List, Any, Optional, Tuple, Literal, Union
from datetime import datetime


# ============= TypedDict Definitions (Internal Use) =============

class LocationDict(TypedDict):
    """Location coordinates as dictionary."""
    latitude: float
    longitude: float


class PlanetaryPositionDict(TypedDict):
    """Planetary position as dictionary (from PlanetaryPosition.to_dict())."""
    name: str
    longitude: float
    latitude: float
    distance: float
    right_ascension: float
    declination: float


class AspectDict(TypedDict):
    """Astrological aspect as dictionary."""
    planet1: str
    planet2: str
    aspect: str  # Conjunction, Sextile, Square, Trine, Opposition
    angle: float  # Actual angle in degrees
    aspect_angle: int  # Expected aspect angle
    orb: float  # Difference from exact aspect


class ChartDict(TypedDict):
    """Complete chart data as dictionary (from ChartData.to_dict())."""
    datetime_utc: str
    location: LocationDict
    planets: Dict[str, PlanetaryPositionDict]
    moon_phase: float
    aspects: List[AspectDict]


class InterpretationDict(TypedDict, total=False):
    """AI interpretation result as dictionary."""
    summary: Optional[str]
    aspects: Optional[str]
    moon_phase: Optional[str]


class ChartResponseDict(TypedDict, total=False):
    """Complete API response dictionary (before Pydantic validation)."""
    datetime_utc: str
    location: LocationDict
    planets: Dict[str, Dict[str, Any]]  # planet_name -> {longitude, latitude, ...}
    moon_phase: float
    moon_phase_name: str
    aspects: List[AspectDict]
    interpretation: Optional[InterpretationDict]


# ============= Type Aliases =============

# Datetime operations
DatetimeInput = Union[datetime, str]  # Can be datetime object or ISO string
DatetimeUTC = datetime  # Always UTC
DateString = str  # ISO format: YYYY-MM-DD HH:MM:SS

# Coordinate types
Latitude = float  # Range: -90 to 90
Longitude = float  # Range: -180 to 180
Coordinates = Tuple[Latitude, Longitude]

# Astrological measurements
Degrees = float  # Angular measurement (0-360)
MoonPhase = float  # Range: 0.0 (new) to 1.0 (new again)
AstronomicalUnit = float  # Distance in AU

# Aspect types
AspectName = Literal["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
AspectAngle = int  # 0, 60, 90, 120, 180

# Data containers
PlanetsDict = Dict[str, PlanetaryPositionDict]  # planet_name -> position
AspectsDict = List[AspectDict]  # List of aspects

# API Provider types
APIProvider = Literal["openai", "anthropic"]


# ============= Validation Functions =============

def validate_latitude(lat: float) -> bool:
    """Check if latitude is valid (-90 to 90)."""
    return -90 <= lat <= 90


def validate_longitude(lon: float) -> bool:
    """Check if longitude is valid (-180 to 180)."""
    return -180 <= lon <= 180


def validate_moon_phase(phase: float) -> bool:
    """Check if moon phase is valid (0 to 1)."""
    return 0.0 <= phase <= 1.0


def validate_degrees(degrees: float) -> bool:
    """Check if angle is valid (0 to 360)."""
    return 0 <= degrees <= 360


# ============= Type Narrowing Functions =============

def is_chart_dict(obj: Any) -> bool:
    """Type guard: Check if object has ChartDict shape."""
    if not isinstance(obj, dict):
        return False
    required_keys = {"datetime_utc", "location", "planets", "moon_phase", "aspects"}
    return required_keys.issubset(obj.keys())


def is_aspect_dict(obj: Any) -> bool:
    """Type guard: Check if object has AspectDict shape."""
    if not isinstance(obj, dict):
        return False
    required_keys = {"planet1", "planet2", "aspect", "angle", "orb"}
    return required_keys.issubset(obj.keys())


def is_planetary_position_dict(obj: Any) -> bool:
    """Type guard: Check if object has PlanetaryPositionDict shape."""
    if not isinstance(obj, dict):
        return False
    required_keys = {"name", "longitude", "latitude", "distance"}
    return required_keys.issubset(obj.keys())


# ============= Conversion Helpers =============

def chart_dict_to_response_dict(
    chart_dict: ChartDict,
    moon_phase_name: str,
    interpretation: Optional[InterpretationDict] = None
) -> ChartResponseDict:
    """
    Convert internal ChartDict to API response format.
    
    Args:
        chart_dict: Internal chart dictionary
        moon_phase_name: Human-readable moon phase name
        interpretation: Optional AI interpretation
    
    Returns:
        Chart response dictionary ready for Pydantic validation
    """
    response: ChartResponseDict = {
        "datetime_utc": chart_dict["datetime_utc"],
        "location": chart_dict["location"],
        "planets": {
            name: {
                "longitude": pos["longitude"],
                "latitude": pos["latitude"],
                "distance_au": pos["distance"],
                "right_ascension": pos["right_ascension"],
                "declination": pos["declination"],
            }
            for name, pos in chart_dict["planets"].items()
        },
        "moon_phase": chart_dict["moon_phase"],
        "moon_phase_name": moon_phase_name,
        "aspects": chart_dict["aspects"],
    }
    
    if interpretation is not None:
        response["interpretation"] = interpretation
    
    return response
