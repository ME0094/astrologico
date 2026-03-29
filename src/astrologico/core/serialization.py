"""
Serialization utilities for chart data.

Handles conversion between ChartData objects and JSON-safe dictionaries.
"""

from typing import Dict, Any
from src.astrologico.core.models import ChartData, PlanetaryPosition


def chart_to_dict(chart: ChartData) -> Dict[str, Any]:
    """
    Convert ChartData object to JSON-safe dictionary.
    
    Args:
        chart: ChartData object
        
    Returns:
        Dictionary with all nested objects converted
    """
    return chart.to_dict()


def planetary_position_to_dict(pos: PlanetaryPosition) -> Dict[str, Any]:
    """
    Convert PlanetaryPosition to dictionary.
    
    Args:
        pos: PlanetaryPosition object
        
    Returns:
        Dictionary representation
    """
    return pos.to_dict()


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
