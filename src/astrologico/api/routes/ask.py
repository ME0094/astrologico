"""
AI question answering routes.

Provides endpoints for answering astrological questions with optional chart context.
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
from src.astrologico.core import (
    AstrologicalCalculator,
    validate_latitude,
    validate_longitude
)
from src.astrologico.ai import AstrologicalInterpreter
from src.astrologico.api.settings import settings

router = APIRouter(prefix="/api/v1", tags=["ai"])

# Initialize components
calculator = AstrologicalCalculator()
interpreter = AstrologicalInterpreter(
    api_provider=settings.ai_provider,
    api_key=settings.openai_api_key or settings.anthropic_api_key
)


def _parse_datetime(datetime_input: DateTimeInput) -> datetime:
    """Parse datetime from input model."""
    if datetime_input.use_now:
        return datetime.utcnow()
    if datetime_input.datetime_str:
        try:
            return datetime.fromisoformat(datetime_input.datetime_str)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid datetime format: {str(e)}"
            )
    raise HTTPException(
        status_code=400,
        detail="Specify datetime_str or set use_now=true"
    )


def _format_chart_for_response(chart) -> dict:
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
    if not interpreter.client:
        raise HTTPException(
            status_code=503,
            detail="AI interpreter not available. Configure API key."
        )
    
    try:
        chart_data = None
        
        # Generate chart context if provided
        if request.datetime and request.location:
            dt = _parse_datetime(request.datetime)
            lat = request.location.latitude
            lon = request.location.longitude
            
            # Validate location
            if not (-90 <= lat <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
            if not (-180 <= lon <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
            
            chart = calculator.generate_chart(dt=dt, lat=lat, lon=lon)
            chart_data = _format_chart_for_response(chart)
        
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
    if not interpreter.client:
        raise HTTPException(
            status_code=503,
            detail="AI interpreter not available. Configure API key."
        )
    
    try:
        # Parse datetimes
        dt1 = _parse_datetime(request.person1_datetime)
        dt2 = _parse_datetime(request.person2_datetime)
        
        lat1 = request.person1_location.latitude
        lon1 = request.person1_location.longitude
        lat2 = request.person2_location.latitude
        lon2 = request.person2_location.longitude
        
        # Validate locations
        for lat in [lat1, lat2]:
            if not (-90 <= lat <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
        for lon in [lon1, lon2]:
            if not (-180 <= lon <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
        
        # Generate charts
        chart1 = calculator.generate_chart(dt=dt1, lat=lat1, lon=lon1)
        chart2 = calculator.generate_chart(dt=dt2, lat=lat2, lon=lon2)
        
        chart1_dict = _format_chart_for_response(chart1)
        chart2_dict = _format_chart_for_response(chart2)
        
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
    if not interpreter.client:
        raise HTTPException(
            status_code=503,
            detail="AI interpreter not available. Configure API key."
        )
    
    try:
        # Parse datetimes
        natal_dt = _parse_datetime(request.natal_datetime)
        transit_dt = _parse_datetime(request.transit_datetime)
        
        lat = request.natal_location.latitude
        lon = request.natal_location.longitude
        
        # Validate location
        if not (-90 <= lat <= 90):
            raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
        
        # Generate charts
        natal_chart = calculator.generate_chart(dt=natal_dt, lat=lat, lon=lon)
        transit_chart = calculator.generate_chart(dt=transit_dt, lat=lat, lon=lon)
        
        natal_dict = _format_chart_for_response(natal_chart)
        transit_dict = _format_chart_for_response(transit_chart)
        
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
