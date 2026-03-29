"""
AI question answering routes.

Provides endpoints for answering astrological questions with optional chart context.
Organized by analysis type: questions, compatibility, transits.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from src.astrologico.api.models import (
    QuestionRequest,
    QuestionResponse,
    DateTimeInput,
    CompatibilityRequest,
    CompatibilityResponse,
    TransitRequest,
    TransitsResponse
)
from src.astrologico.api.dependencies import get_calculator, get_interpreter
from src.astrologico.api.utils import parse_datetime, validate_coordinates

router = APIRouter(prefix="/api/v1", tags=["ai"])


def _get_calculator():
    """Get calculator dependency."""
    return get_calculator()


def _get_interpreter():
    """Get interpreter dependency."""
    return get_interpreter()


def _format_chart_for_response(chart, calculator, interpreter) -> dict:
    """Format ChartData object to dictionary for API response."""
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
    
    return {
        "datetime_utc": chart.datetime_utc,
        "location": {
            "latitude": chart.location_lat,
            "longitude": chart.location_lon
        },
        "planets": planets_data,
        "moon_phase": round(chart.moon_phase, 4),
        "moon_phase_name": interpreter._get_moon_phase_name(chart.moon_phase),
        "aspects": chart.aspects
    }


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask an astrological question with optional chart context.
    
    Args:
        request: QuestionRequest with question and optional chart data
    
    Returns:
        AI answer with optional chart context
    
    Note:
        Requires AI provider API key to be configured
    
    Examples:
        - Simple question: {"question": "What does Mercury retrograde mean?"}
        - With chart context: {"question": "What career path suits me?", "datetime": {...}, "location": {...}}
    """
    calculator = _get_calculator()
    interpreter = _get_interpreter()
    
    if not interpreter.client:
        raise HTTPException(
            status_code=503,
            detail="AI interpreter not available. Configure API key."
        )
    
    try:
        chart_data = None
        
        # Generate chart context if provided
        if request.datetime and request.location:
            dt = parse_datetime(request.datetime)
            lat = request.location.latitude
            lon = request.location.longitude
            
            # Validate location
            validate_coordinates(lat, lon)
            
            chart = calculator.generate_chart(dt=dt, lat=lat, lon=lon)
            chart_data = _format_chart_for_response(chart, calculator, interpreter)
        
        # Answer the question
        answer = interpreter.answer_question(request.question, chart_data)
        
        response_data = {
            "question": request.question,
            "answer": answer
        }
        
        if chart_data:
            response_data["chart_context"] = chart_data
        
        return response_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error answering question: {str(e)}"
        )


@router.post("/analysis/compatibility", response_model=CompatibilityResponse)
async def analyze_compatibility(request: CompatibilityRequest):
    """
    Analyze astrological compatibility between two people.
    
    Args:
        request: CompatibilityRequest with two charts' datetime and location data
    
    Returns:
        Both charts and AI compatibility analysis
    
    Note:
        Requires AI provider API key to be configured
    """
    calculator = _get_calculator()
    interpreter = _get_interpreter()
    
    if not interpreter.client:
        raise HTTPException(
            status_code=503,
            detail="AI interpreter not available. Configure API key."
        )
    
    try:
        # Parse datetimes
        dt1 = parse_datetime(request.person1_datetime)
        dt2 = parse_datetime(request.person2_datetime)
        
        lat1 = request.person1_location.latitude
        lon1 = request.person1_location.longitude
        lat2 = request.person2_location.latitude
        lon2 = request.person2_location.longitude
        
        # Validate locations
        validate_coordinates(lat1, lon1)
        validate_coordinates(lat2, lon2)
        
        # Generate charts
        chart1 = calculator.generate_chart(dt=dt1, lat=lat1, lon=lon1)
        chart2 = calculator.generate_chart(dt=dt2, lat=lat2, lon=lon2)
        
        chart1_dict = _format_chart_for_response(chart1, calculator, interpreter)
        chart2_dict = _format_chart_for_response(chart2, calculator, interpreter)
        
        # Analyze compatibility
        analysis = interpreter.analyze_compatibility(chart1_dict, chart2_dict)
        
        return {
            "person1_chart": chart1_dict,
            "person2_chart": chart2_dict,
            "compatibility_analysis": analysis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing compatibility: {str(e)}"
        )


@router.post("/analysis/transits", response_model=TransitsResponse)
async def analyze_transits(request: TransitRequest):
    """
    Analyze current transits to a natal chart.
    
    Args:
        request: TransitRequest with natal and transit datetimes
    
    Returns:
        Both charts and AI transit analysis
    
    Note:
        Requires AI provider API key to be configured
    """
    calculator = _get_calculator()
    interpreter = _get_interpreter()
    
    if not interpreter.client:
        raise HTTPException(
            status_code=503,
            detail="AI interpreter not available. Configure API key."
        )
    
    try:
        # Parse datetimes
        natal_dt = parse_datetime(request.natal_datetime)
        transit_dt = parse_datetime(request.transit_datetime)
        
        lat = request.natal_location.latitude
        lon = request.natal_location.longitude
        
        # Validate location
        validate_coordinates(lat, lon)
        
        # Generate charts
        natal_chart = calculator.generate_chart(dt=natal_dt, lat=lat, lon=lon)
        transit_chart = calculator.generate_chart(dt=transit_dt, lat=lat, lon=lon)
        
        natal_dict = _format_chart_for_response(natal_chart, calculator, interpreter)
        transit_dict = _format_chart_for_response(transit_chart, calculator, interpreter)
        
        # Generate transit analysis
        prompt = f"""Analyze the transits to a natal chart.

NATAL PLANETS:
{interpreter._format_planets(natal_dict['planets'])}

TRANSIT PLANETS:
{interpreter._format_planets(transit_dict['planets'])}

Provide insights on current transits and their influence on the natal chart."""
        
        analysis = interpreter._query_ai(prompt) if interpreter.client else "Analysis unavailable"
        
        return {
            "natal_chart": natal_dict,
            "transit_chart": transit_dict,
            "transit_analysis": analysis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing transits: {str(e)}"
        )
