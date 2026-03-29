"""
Serialization utilities for chart data.

Handles conversion between ChartData objects and JSON-safe dictionaries
with complete type safety using TypedDict definitions.
"""

from typing import Dict, Any
from src.astrologico.core.models import ChartData, PlanetaryPosition
from src.astrologico.core.types import ChartDict, PlanetaryPositionDict


def chart_to_dict(chart: ChartData) -> ChartDict:
    """
    Convert ChartData object to JSON-safe TypedDict.
    
    Args:
        chart: ChartData object
        
    Returns:
        ChartDict with all nested objects converted
    """
    return chart.to_dict()  # type: ignore


def planetary_position_to_dict(pos: PlanetaryPosition) -> PlanetaryPositionDict:
    """
    Convert PlanetaryPosition to TypedDict.
    
    Args:
        pos: PlanetaryPosition object
        
    Returns:
        PlanetaryPositionDict representation
    """
    return pos.to_dict()  # type: ignore


def format_chart_output(chart: ChartData) -> str:
    """
    Format chart data as human-readable text.
    
    Args:
        chart: ChartData object
        
    Returns:
        Formatted string for display
    """
    from src.astrologico.core.calculator import AstrologicalCalculator
    
    calc = AstrologicalCalculator()
    output = []
    output.append("\n" + "=" * 70)
    output.append("ASTROLOGICAL CHART")
    output.append("=" * 70)
    output.append(f"Date/Time: {chart.datetime_utc}")
    output.append(f"Location: {chart.location_lat}°, {chart.location_lon}°")
    output.append(f"Moon Phase: {chart.moon_phase:.2%} illuminated")
    output.append("")

    output.append("PLANETARY POSITIONS:")
    output.append("-" * 70)

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
