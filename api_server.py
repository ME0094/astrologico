#!/usr/bin/env python3
"""
REST API for Astrologico with AI-powered features.
Built with FastAPI for high-performance astrological analysis.
"""

from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel
import json
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from astrologico import AstrologicalCalculator, ChartData
from ai_interpreter import AstrologicalInterpreter

# ============= Pydantic Models =============

class LocationInput(BaseModel):
    """Location coordinates."""
    latitude: float
    longitude: float
    name: Optional[str] = "Unknown"


class DateTimeInput(BaseModel):
    """DateTime specification."""
    datetime_str: str  # ISO format: YYYY-MM-DD HH:MM:SS
    use_now: bool = False


class ChartRequest(BaseModel):
    """Request for astrological chart."""
    datetime: DateTimeInput
    location: LocationInput
    include_interpretation: bool = True


class CompatibilityRequest(BaseModel):
    """Request for compatibility analysis."""
    person1_datetime: DateTimeInput
    person1_location: LocationInput
    person2_datetime: DateTimeInput
    person2_location: LocationInput


class QuestionRequest(BaseModel):
    """Natural language question."""
    question: str
    datetime: Optional[DateTimeInput] = None
    location: Optional[LocationInput] = None


class TransitRequest(BaseModel):
    """Transit analysis request."""
    natal_datetime: DateTimeInput
    natal_location: LocationInput
    transit_datetime: DateTimeInput


# ============= API Application =============

app = FastAPI(
    title="Astrologico AI API",
    description="Professional astrological calculation and AI interpretation service",
    version="2.0.0"
)

# Enable CORS with configurable origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize components
calculator = AstrologicalCalculator()
interpreter = AstrologicalInterpreter()


# ============= Helper Functions =============

def parse_datetime(datetime_input: DateTimeInput) -> datetime:
    """Parse datetime from input."""
    if datetime_input.use_now:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(datetime_input.datetime_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")


def format_chart_for_response(chart: ChartData) -> Dict:
    """Format chart data for JSON response."""
    planets_data = {}
    for name, pos in chart.planets.items():
        planets_data[name] = {
            'longitude': pos.longitude,
            'latitude': pos.latitude,
            'distance_au': pos.distance,
            'right_ascension': pos.right_ascension,
            'declination': pos.declination,
            'zodiac_sign': calculator.get_zodiac_sign(pos.longitude)[0],
            'sign_position': round(calculator.get_zodiac_sign(pos.longitude)[1], 2)
        }
    
    return {
        'datetime_utc': chart.datetime_utc,
        'location': {
            'latitude': chart.location_lat,
            'longitude': chart.location_lon
        },
        'planets': planets_data,
        'moon_phase': round(chart.moon_phase, 4),
        'moon_phase_name': interpreter._get_moon_phase_name(chart.moon_phase),
        'aspects': chart.aspects
    }


# ============= Root Endpoints =============

@app.get("/")
async def root():
    """API information."""
    return {
        "name": "Astrologico AI API",
        "version": "2.0.0",
        "description": "Professional astrological calculations with AI interpretation",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "calculator": "ready",
        "interpreter": "ready" if interpreter.client else "no API key"
    }


# ============= Chart Endpoints =============

@app.post("/api/v1/chart/generate")
async def generate_chart(request: ChartRequest):
    """
    Generate a complete astrological chart.
    
    Returns:
    - Planetary positions
    - Aspects
    - Moon phase
    - AI interpretation (if enabled)
    """
    try:
        dt = parse_datetime(request.datetime)
        chart = calculator.generate_chart(
            dt=dt,
            lat=request.location.latitude,
            lon=request.location.longitude
        )
        
        response = format_chart_for_response(chart)
        
        # Add AI interpretation if requested
        if request.include_interpretation and interpreter.client:
            response['interpretation'] = {
                'summary': interpreter.generate_chart_summary(response),
                'aspects': interpreter.interpret_aspects(chart.aspects),
                'moon_phase': interpreter.interpret_moon_phase(chart.moon_phase)
            }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/chart/quick")
async def quick_chart(
    now: bool = Query(False, description="Use current UTC time"),
    date: Optional[str] = Query(None, description="ISO datetime string"),
    lat: float = Query(0.0, description="Latitude"),
    lon: float = Query(0.0, description="Longitude"),
    json_output: bool = Query(False, description="Skip interpretation")
):
    """Quick chart generation via query parameters."""
    try:
        if now:
            dt = datetime.utcnow()
        elif date:
            dt = datetime.fromisoformat(date)
        else:
            raise HTTPException(status_code=400, detail="Specify 'now' or 'date' parameter")
        
        chart = calculator.generate_chart(dt=dt, lat=lat, lon=lon)
        response = format_chart_for_response(chart)
        
        if not json_output and interpreter.client:
            response['interpretation'] = {
                'aspects': interpreter.interpret_aspects(chart.aspects),
                'moon': interpreter.interpret_moon_phase(chart.moon_phase)
            }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Interpretation Endpoints =============

@app.post("/api/v1/interpret/aspects")
async def interpret_aspects(aspects: List[Dict]):
    """Get AI interpretation of aspects."""
    if not interpreter.client:
        raise HTTPException(status_code=503, detail="AI interpreter not available")
    
    try:
        interpretation = interpreter.interpret_aspects(aspects)
        return {
            "aspects": aspects,
            "interpretation": interpretation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/interpret/moon")
async def interpret_moon(phase: float = Query(..., description="Moon phase 0-1")):
    """Get AI interpretation of moon phase."""
    if not interpreter.client:
        raise HTTPException(status_code=503, detail="AI interpreter not available")
    
    if not (0 <= phase <= 1):
        raise HTTPException(status_code=400, detail="Phase must be between 0 and 1")
    
    try:
        interpretation = interpreter.interpret_moon_phase(phase)
        return {
            "moon_phase": phase,
            "phase_name": interpreter._get_moon_phase_name(phase),
            "interpretation": interpretation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Analysis Endpoints =============

@app.post("/api/v1/analysis/compatibility")
async def analyze_compatibility(request: CompatibilityRequest):
    """Analyze astrological compatibility between two people."""
    if not interpreter.client:
        raise HTTPException(status_code=503, detail="AI interpreter not available")
    
    try:
        dt1 = parse_datetime(request.person1_datetime)
        dt2 = parse_datetime(request.person2_datetime)
        
        chart1 = calculator.generate_chart(
            dt=dt1,
            lat=request.person1_location.latitude,
            lon=request.person1_location.longitude
        )
        chart2 = calculator.generate_chart(
            dt=dt2,
            lat=request.person2_location.latitude,
            lon=request.person2_location.longitude
        )
        
        chart1_dict = format_chart_for_response(chart1)
        chart2_dict = format_chart_for_response(chart2)
        
        analysis = interpreter.analyze_compatibility(chart1_dict, chart2_dict)
        
        return {
            "person1_chart": chart1_dict,
            "person2_chart": chart2_dict,
            "compatibility_analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analysis/transits")
async def analyze_transits(request: TransitRequest):
    """Analyze current transits to natal chart."""
    if not interpreter.client:
        raise HTTPException(status_code=503, detail="AI interpreter not available")
    
    try:
        natal_dt = parse_datetime(request.natal_datetime)
        transit_dt = parse_datetime(request.transit_datetime)
        
        natal_chart = calculator.generate_chart(
            dt=natal_dt,
            lat=request.natal_location.latitude,
            lon=request.natal_location.longitude
        )
        transit_chart = calculator.generate_chart(
            dt=transit_dt,
            lat=request.natal_location.latitude,
            lon=request.natal_location.longitude
        )
        
        prompt = f"""Analyze the transits to a natal chart.
        
NATAL PLANETS:
{interpreter._format_planets(format_chart_for_response(natal_chart)['planets'])}

TRANSIT PLANETS:
{interpreter._format_planets(format_chart_for_response(transit_chart)['planets'])}

Provide insights on current transits and their influence on the natal chart."""
        
        analysis = interpreter._query_ai(prompt) if interpreter.client else "Analysis unavailable"
        
        return {
            "natal_chart": format_chart_for_response(natal_chart),
            "transit_chart": format_chart_for_response(transit_chart),
            "transit_analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Q&A Endpoint =============

@app.post("/api/v1/ask")
async def ask_question(request: QuestionRequest):
    """
    Ask any astrological question with optional chart context.
    Leverages AI for thoughtful responses.
    """
    if not interpreter.client:
        raise HTTPException(status_code=503, detail="AI interpreter not available")
    
    try:
        chart_data = None
        
        if request.datetime and request.location:
            dt = parse_datetime(request.datetime)
            chart = calculator.generate_chart(
                dt=dt,
                lat=request.location.latitude,
                lon=request.location.longitude
            )
            chart_data = format_chart_for_response(chart)
        
        answer = interpreter.answer_question(request.question, chart_data)
        
        response_data = {
            "question": request.question,
            "answer": answer
        }
        
        if chart_data:
            response_data["chart_context"] = chart_data
        
        return response_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Planetary Data Endpoints =============

@app.get("/api/v1/planets")
async def get_planets(
    now: bool = Query(False),
    date: Optional[str] = Query(None),
    lat: float = Query(0.0),
    lon: float = Query(0.0)
):
    """Get current planetary positions."""
    try:
        if now:
            dt = datetime.utcnow()
        elif date:
            dt = datetime.fromisoformat(date)
        else:
            dt = datetime.utcnow()
        
        positions = calculator.calculate_planetary_positions(dt=dt, lat=lat, lon=lon)
        
        return {
            "datetime_utc": dt.isoformat(),
            "location": {"latitude": lat, "longitude": lon},
            "planets": {
                name: {
                    "longitude": pos.longitude,
                    "latitude": pos.latitude,
                    "distance_au": pos.distance
                }
                for name, pos in positions.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/aspects")
async def get_aspects(
    now: bool = Query(False),
    date: Optional[str] = Query(None),
    lat: float = Query(0.0),
    lon: float = Query(0.0),
    orb: float = Query(8.0)
):
    """Calculate planetary aspects."""
    try:
        if now:
            dt = datetime.utcnow()
        elif date:
            dt = datetime.fromisoformat(date)
        else:
            dt = datetime.utcnow()
        
        positions = calculator.calculate_planetary_positions(dt=dt, lat=lat, lon=lon)
        aspects = calculator.calculate_aspects(positions, orb=orb)
        
        return {
            "datetime_utc": dt.isoformat(),
            "orb": orb,
            "aspects_count": len(aspects),
            "aspects": aspects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/moon")
async def get_moon(
    now: bool = Query(False),
    date: Optional[str] = Query(None)
):
    """Get moon phase information."""
    try:
        if now:
            dt = datetime.utcnow()
        elif date:
            dt = datetime.fromisoformat(date)
        else:
            dt = datetime.utcnow()
        
        phase = calculator.calculate_moon_phase(dt)
        phase_name = interpreter._get_moon_phase_name(phase)
        
        return {
            "datetime_utc": dt.isoformat(),
            "phase": round(phase, 4),
            "phase_name": phase_name,
            "illumination": f"{phase * 100:.1f}%"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Status & Configuration =============

@app.get("/api/v1/status")
async def get_status():
    """Get API and interpreter status."""
    return {
        "api_version": "2.0.0",
        "calculator_status": "operational",
        "interpreter_status": "operational" if interpreter.client else "no_api_key",
        "interpreter_provider": interpreter.api_provider,
        "ai_features_enabled": bool(interpreter.client),
        "endpoints": {
            "chart": "/api/v1/chart/generate",
            "compatibility": "/api/v1/analysis/compatibility",
            "transits": "/api/v1/analysis/transits",
            "ask": "/api/v1/ask",
            "documentation": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
