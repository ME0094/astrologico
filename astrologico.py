#!/usr/bin/env python3
"""
Astrologico - Professional Astrological Calculation Suite for Debian
Comprehensive toolkit for planetary positions, aspects, charts, and more.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

import ephem
import numpy as np
from skyfield import api, almanac

# Load ephemeris data
ts = api.load.timescale()
eph = api.load('de421.bsp')
earth = eph['earth']
sun = eph['sun']
moon = eph['moon']


@dataclass
class PlanetaryPosition:
    """Represents a planetary position."""
    name: str
    longitude: float  # In degrees
    latitude: float
    distance: float  # In AU
    right_ascension: float  # In hours
    declination: float  # In degrees


@dataclass
class ChartData:
    """Represents astrological chart data."""
    datetime_utc: str
    location_lat: float
    location_lon: float
    planets: Dict[str, PlanetaryPosition]
    moon_phase: float  # 0-1 (new to full)
    aspects: List[Dict]


class AstrologicalCalculator:
    """Main astrological calculator class."""

    def __init__(self):
        """Initialize the calculator."""
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
            dt: UTC datetime
            lat: Observer latitude (degrees)
            lon: Observer longitude (degrees)

        Returns:
            Dictionary of planetary positions
        """
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.date = dt

        positions = {}
        planet_names = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']

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

            # Extract coordinates
            lon_str = str(planet_obj.ra)  # Right Ascension
            lat_str = str(planet_obj.dec)  # Declination

            positions[name] = PlanetaryPosition(
                name=name,
                longitude=float(planet_obj.hlon),  # Ecliptic longitude
                latitude=float(planet_obj.hlat),   # Ecliptic latitude
                distance=float(planet_obj.sun_distance),
                right_ascension=float(planet_obj.a_ra),
                declination=float(planet_obj.a_dec)
            )

        return positions

    def calculate_moon_phase(self, dt: datetime) -> float:
        """
        Calculate moon phase (0.0=new, 0.5=full, 1.0=new again).

        Args:
            dt: UTC datetime

        Returns:
            Moon phase as float 0-1
        """
        # Use ephem for moon phase calculation via Sun/Moon positions
        observer = ephem.Observer()
        observer.date = dt
        
        sun = ephem.Sun(observer)
        moon = ephem.Moon(observer)
        
        # Calculate phase as elongation / 180 degrees
        # Elongation is angular separation between Sun and Moon
        separation = float(ephem.separation(sun, moon)) * 180.0 / np.pi
        
        # Normalize to 0-1 (0=new, 0.5=full)
        phase = (separation + 180.0) % 360.0 / 360.0
        
        return phase

    def calculate_aspects(self, positions: Dict[str, PlanetaryPosition],
                         orb: float = 8.0) -> List[Dict]:
        """
        Calculate aspects between planets.

        Args:
            positions: Dictionary of planetary positions
            orb: Orb in degrees (default 8)

        Returns:
            List of aspects
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
            for name2, pos2 in planet_list[i+1:]:
                diff = abs(pos1.longitude - pos2.longitude)
                # Normalize to 0-180
                if diff > 180:
                    diff = 360 - diff

                # Check for aspects
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
            Tuple of (sign name, position in sign)
        """
        signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        normalized = longitude % 360
        sign_index = int(normalized / 30)
        position = normalized % 30

        return signs[sign_index], round(position, 2)

    def generate_chart(self, dt: datetime, lat: float = 0.0,
                      lon: float = 0.0) -> ChartData:
        """
        Generate a complete astrological chart.

        Args:
            dt: UTC datetime
            lat: Observer latitude
            lon: Observer longitude

        Returns:
            Complete chart data
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


def format_chart_output(chart: ChartData) -> str:
    """Format chart data for display."""
    output = []
    output.append("\n" + "="*70)
    output.append("ASTROLOGICAL CHART")
    output.append("="*70)
    output.append(f"Date/Time: {chart.datetime_utc}")
    output.append(f"Location: {chart.location_lat}°, {chart.location_lon}°")
    output.append(f"Moon Phase: {chart.moon_phase:.2%} illuminated")
    output.append("")

    output.append("PLANETARY POSITIONS:")
    output.append("-" * 70)

    calc = AstrologicalCalculator()
    for name, pos in chart.planets.items():
        sign, sign_pos = calc.get_zodiac_sign(pos.longitude)
        output.append(
            f"{name:10} | {pos.longitude:7.2f}° ({sign} {sign_pos:5.2f}°) | "
            f"Dist: {pos.distance:7.4f} AU"
        )

    output.append("")
    output.append("ASPECTS:")
    output.append("-" * 70)
    if chart.aspects:
        for aspect in chart.aspects:
            output.append(
                f"{aspect['planet1']:10} {aspect['aspect']:12} {aspect['planet2']:10} "
                f"| Angle: {aspect['angle']:6.2f}° (Orb: {aspect['orb']:5.2f}°)"
            )
    else:
        output.append("No major aspects found within orb.")

    output.append("=" * 70 + "\n")
    return "\n".join(output)


if __name__ == "__main__":
    # Example usage
    now = datetime.utcnow()
    calc = AstrologicalCalculator()
    chart = calc.generate_chart(now, lat=40.7128, lon=-74.0060)  # NYC

    print(format_chart_output(chart))
    print("\nJSON Output:")
    print(json.dumps(
        {
            'datetime': chart.datetime_utc,
            'location': {'lat': chart.location_lat, 'lon': chart.location_lon},
            'moon_phase': chart.moon_phase,
            'planets': {
                name: {
                    'longitude': pos.longitude,
                    'latitude': pos.latitude,
                    'distance': pos.distance
                }
                for name, pos in chart.planets.items()
            },
            'aspects_count': len(chart.aspects)
        },
        indent=2
    ))
