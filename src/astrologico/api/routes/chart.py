"""
Astrological chart routes.

Provides endpoints for chart generation and interpretation.
Routes are organized by chart-related operations.
"""

from datetime import datetime
from typing import Optional, Any
from fastapi import APIRouter, HTTPException, Query
from astrologico.api.models import (
    ChartRequest,
    DateTimeInput,
    LocationInput,
    ChartResponse,
    PlanetaryData,
    LocationData,
    AspectData
)
from astrologico.api.dependencies import get_calculator, get_interpreter
from astrologico.api.utils import parse_datetime, validate_coordinates
from astrologico.core import AspectDict

router = APIRouter(prefix="/api/v1", tags=["chart"])


def _get_calculator():
    """Get calculator dependency."""
    return get_calculator()


def _get_interpreter():
    """Get interpreter dependency."""
    return get_interpreter()


def _format_chart_for_response(chart: Any, calculator: Any, interpreter: Any) -> dict:  # Returns dict ready for Pydantic validation
    """Format ChartData object to dictionary."""
    planets_data = {}
    for name, pos in chart.planets.items():
        sign, sign_pos = calculator.get_zodiac_sign(pos.longitude)
        planets_data[name] = {
            "longitude": pos.longitude,
            "latitude": pos.latitude,
            "distance_au": pos.distance,
            "right_ascension": pos.right_ascension,
            "declination": pos.declination,
            "zodiac_sign": sign,
            "sign_position": round(sign_pos, 2)
        }
    
    # Convert aspects
    aspects_data = [AspectData(**aspect) for aspect in chart.aspects]
    
    return {
        "datetime_utc": chart.datetime_utc,
        "location": {
            "latitude": chart.location_lat,
            "longitude": chart.location_lon
        },
        "planets": planets_data,
        "moon_phase": round(chart.moon_phase, 4),
        "moon_phase_name": interpreter._get_moon_phase_name(chart.moon_phase),
        "aspects": aspects_data
    }


@router.post("/chart/generate", response_model=ChartResponse)
async def generate_chart(request: ChartRequest):
    """
    Generate a complete astrological chart.
    
    Args:
        request: ChartRequest with datetime and location
    
    Returns:
        Complete chart data including planetary positions, aspects, and moon phase
    
    Note:
        Set include_interpretation=true to add AI insights (requires API key)
    """
    try:
        calculator = _get_calculator()
        interpreter = _get_interpreter()
        
        # Parse datetime
        dt = parse_datetime(request.datetime)
        
        # Validate location
        lat = request.location.latitude
        lon = request.location.longitude
        validate_coordinates(lat, lon)
        
        # Generate chart
        chart = calculator.generate_chart(dt=dt, lat=lat, lon=lon)
        response = _format_chart_for_response(chart, calculator, interpreter)
        
        # Add AI interpretation if requested
        if request.include_interpretation and interpreter.client:
            response['interpretation'] = {
                'summary': interpreter.generate_chart_summary(response),
                'aspects': interpreter.interpret_aspects(chart.aspects),
                'moon_phase': interpreter.interpret_moon_phase(chart.moon_phase)
            }
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating chart: {str(e)}"
        )


@router.get("/chart/quick", response_model=ChartResponse)
async def quick_chart(
    now: bool = Query(False, description="Use current UTC time"),
    date: Optional[str] = Query(None, description="ISO datetime string"),
    lat: float = Query(0.0, description="Observer latitude"),
    lon: float = Query(0.0, description="Observer longitude"),
    no_interpretation: bool = Query(False, description="Skip AI interpretation")
):
    """
    Quick chart generation with query parameters.
    
    Args:
        now: Use current UTC time
        date: ISO datetime string (YYYY-MM-DD HH:MM:SS)
        lat: Observer latitude
        lon: Observer longitude
        no_interpretation: Skip AI interpretation if true
    
    Returns:
        Complete astrological chart
    
    Example:
        /api/v1/chart/quick?now=true&lat=40.7128&lon=-74.0060
    """
    try:
        calculator = _get_calculator()
        interpreter = _get_interpreter()
        
        # Parse datetime
        if now:
            dt = datetime.utcnow()
        elif date:
            try:
                dt = datetime.fromisoformat(date)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid datetime format. Use: YYYY-MM-DD HH:MM:SS"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Specify 'now=true' or 'date' parameter"
            )
        
        # Validate location
        validate_coordinates(lat, lon)
        
        # Generate chart
        chart = calculator.generate_chart(dt=dt, lat=lat, lon=lon)
        response = _format_chart_for_response(chart, calculator, interpreter)
        
        # Add interpretation unless skipped
        if not no_interpretation and interpreter.client:
            response['interpretation'] = {
                'aspects': interpreter.interpret_aspects(chart.aspects),
                'moon_phase': interpreter.interpret_moon_phase(chart.moon_phase)
            }
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating chart: {str(e)}"
        )
