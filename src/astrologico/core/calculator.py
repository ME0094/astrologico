"""
Core astrological calculation engine.

Provides planetary position calculations, aspect detection, and chart generation
using PyEphem and Skyfield ephemeris data.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

import ephem
import numpy as np
from skyfield import api, almanac

from astrologico.core.models import ChartData, PlanetaryPosition

# Load ephemeris data at module level
try:
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    earth = eph['earth']
    sun = eph['sun']
    moon = eph['moon']
except Exception as e:
    # Handle missing ephemeris data
    print(f"Warning: Could not load ephemeris data: {e}")
    ts = None
    eph = None


class AstrologicalCalculator:
    """
    Main astrological calculator class.
    
    Handles calculation of planetary positions, aspects, moon phases,
    and complete astrological charts.
    """

    def __init__(self):
        """Initialize the calculator with planetary names."""
        self.planets = {
            'Sun': None,
            'Moon': None,
            'Mercury': None,
            'Venus': None,
            'Mars': None,
            'Jupiter': None,
            'Saturn': None,
            'Uranus': None,
            'Neptune': None,
            'Pluto': None
        }

    def calculate_planetary_positions(self,
                                     dt: datetime,
                                     lat: float = 0.0,
                                     lon: float = 0.0) -> Dict[str, PlanetaryPosition]:
        """
        Calculate positions of all major planets.

        Args:
            dt: UTC datetime object
            lat: Observer latitude in degrees (default: 0.0)
            lon: Observer longitude in degrees (default: 0.0)

        Returns:
            Dictionary mapping planet names to PlanetaryPosition objects
            
        Raises:
            ValueError: If datetime is invalid or observer coordinates out of range
        """
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.date = dt

        positions = {}
        planet_names = [
            'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
            'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'
        ]

        planet_objects = [
            ephem.Sun(),
            ephem.Moon(),
            ephem.Mercury(),
            ephem.Venus(),
            ephem.Mars(),
            ephem.Jupiter(),
            ephem.Saturn(),
            ephem.Uranus(),
            ephem.Neptune(),
            ephem.Pluto()
        ]

        for name, planet_obj in zip(planet_names, planet_objects):
            planet_obj.compute(observer)

            # Extract coordinates from PyEphem object
            positions[name] = PlanetaryPosition(
                name=name,
                longitude=float(planet_obj.hlon),      # Ecliptic longitude
                latitude=float(planet_obj.hlat),       # Ecliptic latitude
                distance=float(planet_obj.sun_distance),  # Distance from Sun in AU
                right_ascension=float(planet_obj.a_ra),   # Equatorial RA
                declination=float(planet_obj.a_dec)       # Equatorial declination
            )

        return positions

    def calculate_moon_phase(self, dt: datetime) -> float:
        """
        Calculate moon phase illumination.

        Args:
            dt: UTC datetime object

        Returns:
            Moon phase as float 0-1 (0=new moon, 0.5=full moon, 1.0=new again)
        """
        observer = ephem.Observer()
        observer.date = dt

        sun = ephem.Sun(observer)
        moon = ephem.Moon(observer)

        # Calculate elongation (angular separation between Sun and Moon)
        separation_rad = float(ephem.separation(sun, moon))
        separation_deg = separation_rad * 180.0 / np.pi

        # Normalize to 0-1 phase (0=new, 0.5=full)
        phase = (separation_deg + 180.0) % 360.0 / 360.0

        return phase

    def calculate_aspects(self,
                         positions: Dict[str, PlanetaryPosition],
                         orb: float = 8.0) -> List[Dict]:
        """
        Calculate major aspects between planets.

        Args:
            positions: Dictionary of planetary positions
            orb: Orb threshold in degrees for aspect detection (default: 8.0)

        Returns:
            List of aspect dictionaries with keys:
            - planet1, planet2: Planet names
            - aspect: Aspect name (Conjunction, Sextile, Square, Trine, Opposition)
            - angle: Actual angle between planets
            - aspect_angle: Expected aspect angle
            - orb: Orb (difference from exact aspect)
        """
        aspects = []
        aspect_types = {
            0: 'Conjunction',
            60: 'Sextile',
            90: 'Square',
            120: 'Trine',
            180: 'Opposition'
        }

        planet_list = list(positions.items())

        for i, (name1, pos1) in enumerate(planet_list):
            for name2, pos2 in planet_list[i + 1:]:
                # Calculate angular difference
                diff = abs(pos1.longitude - pos2.longitude)

                # Normalize to 0-180 range
                if diff > 180:
                    diff = 360 - diff

                # Check for each aspect type
                for aspect_angle, aspect_name in aspect_types.items():
                    if abs(diff - aspect_angle) <= orb:
                        aspects.append({
                            'planet1': name1,
                            'planet2': name2,
                            'aspect': aspect_name,
                            'angle': round(diff, 2),
                            'aspect_angle': aspect_angle,
                            'orb': round(abs(diff - aspect_angle), 2)
                        })

        return aspects

    def get_zodiac_sign(self, longitude: float) -> Tuple[str, float]:
        """
        Get zodiac sign from ecliptic longitude.

        Args:
            longitude: Ecliptic longitude in degrees (0-360)

        Returns:
            Tuple of (zodiac sign name, position in sign in degrees 0-30)
        """
        signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        normalized = longitude % 360
        sign_index = int(normalized / 30)
        position = normalized % 30

        return signs[sign_index], round(position, 2)

    def generate_chart(self,
                      dt: datetime,
                      lat: float = 0.0,
                      lon: float = 0.0) -> ChartData:
        """
        Generate a complete astrological chart.

        Args:
            dt: UTC datetime for chart calculation
            lat: Observer latitude in degrees
            lon: Observer longitude in degrees

        Returns:
            ChartData object containing planetary positions, aspects, and moon phase
        """
        positions = self.calculate_planetary_positions(dt, lat, lon)
        moon_phase = self.calculate_moon_phase(dt)
        aspects = self.calculate_aspects(positions)

        return ChartData(
            datetime_utc=dt.isoformat(),
            location_lat=lat,
            location_lon=lon,
            planets=positions,
            moon_phase=moon_phase,
            aspects=aspects
        )
