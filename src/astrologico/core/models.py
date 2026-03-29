"""
Data models for astrological calculations.

Defines TypedDict and dataclass models for planetary positions, chart data,
and API responses with proper type hints.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class AspectType(str, Enum):
    """Astrological aspect types."""
    CONJUNCTION = "Conjunction"
    SEXTILE = "Sextile"
    SQUARE = "Square"
    TRINE = "Trine"
    OPPOSITION = "Opposition"


@dataclass
class PlanetaryPosition:
    """
    Represents a planetary position in space.
    
    Attributes:
        name: Planet name (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto)
        longitude: Ecliptic longitude in degrees (0-360)
        latitude: Ecliptic latitude in degrees (-90 to 90)
        distance: Distance from Earth in Astronomical Units (AU)
        right_ascension: Right ascension in hours
        declination: Declination in degrees
    """
    name: str
    longitude: float
    latitude: float
    distance: float
    right_ascension: float
    declination: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "longitude": round(self.longitude, 4),
            "latitude": round(self.latitude, 4),
            "distance": round(self.distance, 4),
            "right_ascension": round(self.right_ascension, 4),
            "declination": round(self.declination, 4),
        }


@dataclass
class ChartData:
    """
    Represents astrological chart data.
    
    Contains all calculated planetary positions, aspects, and moon phase
    for a specific date, time, and location.
    
    Attributes:
        datetime_utc: ISO format UTC datetime
        location_lat: Observer latitude in degrees
        location_lon: Observer longitude in degrees
        planets: Dictionary mapping planet names to PlanetaryPosition objects
        moon_phase: Moon phase as fractional illumination (0.0=new, 0.5=full, 1.0=new)
        aspects: List of astrological aspects
    """
    datetime_utc: str
    location_lat: float
    location_lon: float
    planets: Dict[str, PlanetaryPosition]
    moon_phase: float
    aspects: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to JSON-safe dictionary for serialization.
        
        Returns:
            Dictionary with all nested dataclasses converted to dicts
        """
        return {
            "datetime_utc": self.datetime_utc,
            "location": {
                "latitude": self.location_lat,
                "longitude": self.location_lon,
            },
            "planets": {
                name: pos.to_dict()
                for name, pos in self.planets.items()
            },
            "moon_phase": round(self.moon_phase, 4),
            "aspects": self.aspects,
        }


class AspectData:
    """Represents an astrological aspect between two planets."""
    
    def __init__(
        self,
        planet1: str,
        planet2: str,
        aspect_type: AspectType,
        angle: float,
        orb: float
    ):
        """
        Initialize aspect data.
        
        Args:
            planet1: Name of first planet
            planet2: Name of second planet
            aspect_type: Type of aspect
            angle: Actual angle between planets in degrees
            orb: Orb (difference from exact aspect angle)
        """
        self.planet1 = planet1
        self.planet2 = planet2
        self.aspect_type = aspect_type
        self.angle = round(angle, 2)
        self.orb = round(orb, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "planet1": self.planet1,
            "planet2": self.planet2,
            "aspect": self.aspect_type.value,
            "angle": self.angle,
            "orb": self.orb,
        }
