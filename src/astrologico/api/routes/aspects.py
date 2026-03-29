"""
Aspect calculation routes.

Provides endpoints for planetary aspect detection and analysis.
"""

from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException, Query
from src.astrologico.api.models import AspectsResponse, AspectData, AspectsInterpretationResponse
from src.astrologico.core import AstrologicalCalculator
from src.astrologico.ai import AstrologicalInterpreter
from src.astrologico.api.settings import settings

router = APIRouter(prefix="/api/v1", tags=["aspects"])

# Initialize components
calculator = AstrologicalCalculator()
interpreter = AstrologicalInterpreter(
    api_provider=settings.ai_provider,
    api_key=settings.openai_api_key or settings.anthropic_api_key
)


@router.get("/aspects", response_model=AspectsResponse)
async def get_aspects(
    now: bool = Query(False, description="Use current UTC time"),
    date: Optional[str] = Query(None, description="ISO datetime string"),
    lat: float = Query(0.0, description="Observer latitude"),
    lon: float = Query(0.0, description="Observer longitude"),
    orb: float = Query(8.0, description="Aspect orb in degrees")
):
    """
    Calculate planetary aspects at a specific time and location.
    
    Args:
        now: Use current UTC time
        date: ISO datetime string
        lat: Observer latitude
        lon: Observer longitude
        orb: Orb threshold for aspect detection (1-12 degrees)
    
    Returns:
        List of planetary aspects with angles and orbs
    """
    try:
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
            dt = datetime.utcnow()
        
        # Validate location
        if not (-90 <= lat <= 90):
            raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
        
        # Validate orb
        if not (1 <= orb <= 12):
            raise HTTPException(status_code=400, detail="Orb must be between 1 and 12 degrees")
        
        # Calculate positions and aspects
        positions = calculator.calculate_planetary_positions(dt=dt, lat=lat, lon=lon)
        aspects = calculator.calculate_aspects(positions, orb=orb)
        
        # Convert to response model
        aspect_data = [AspectData(**aspect) for aspect in aspects]
        
        return {
            "datetime_utc": dt.isoformat(),
            "orb": orb,
            "aspects_count": len(aspects),
            "aspects": aspect_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating aspects: {str(e)}"
        )


@router.post("/interpret/aspects", response_model=AspectsInterpretationResponse)
async def interpret_aspects(aspects: List[Dict]):
    """
    Get AI interpretation of planetary aspects.
    
    Args:
        aspects: List of aspect dictionaries
    
    Returns:
        AI interpretation of the aspects
    
    Note:
        Requires AI provider API key to be configured
    """
    if not interpreter.client:
        raise HTTPException(
            status_code=503,
            detail="AI interpreter not available. Configure API key."
        )
    
    try:
        if not aspects:
            raise HTTPException(status_code=400, detail="No aspects provided")
        
        interpretation = interpreter.interpret_aspects(aspects)
        
        return {
            "aspects": aspects,
            "interpretation": interpretation
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interpreting aspects: {str(e)}"
        )
