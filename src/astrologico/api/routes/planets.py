"""
Planetary position routes.

Provides endpoints for planetary position calculations.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from src.astrologico.api.models import PlanetsResponse
from src.astrologico.core import AstrologicalCalculator

router = APIRouter(prefix="/api/v1", tags=["planets"])

# Initialize calculator
calculator = AstrologicalCalculator()


@router.get("/planets", response_model=PlanetsResponse)
async def get_planets(
    now: bool = Query(False, description="Use current UTC time"),
    date: Optional[str] = Query(None, description="ISO datetime string (YYYY-MM-DD HH:MM:SS)"),
    lat: float = Query(0.0, description="Observer latitude (-90 to 90)"),
    lon: float = Query(0.0, description="Observer longitude (-180 to 180)")
):
    """
    Get planetary positions at a specific time and location.
    
    Args:
        now: Use current UTC time
        date: ISO datetime string (e.g., "2024-01-15 12:30:45")
        lat: Observer latitude
        lon: Observer longitude
    
    Returns:
        Planetary positions with coordinates and distances
    """
    try:
        # Parse datetime
        if now:
            dt: datetime = datetime.utcnow()
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
        
        # Calculate positions
        positions = calculator.calculate_planetary_positions(dt=dt, lat=lat, lon=lon)
        
        planets_data = {}
        for name, pos in positions.items():
            planets_data[name] = {
                "longitude": pos.longitude,
                "latitude": pos.latitude,
                "distance_au": pos.distance,
                "right_ascension": pos.right_ascension,
                "declination": pos.declination,
                "zodiac_sign": calculator.get_zodiac_sign(pos.longitude)[0],
                "sign_position": round(calculator.get_zodiac_sign(pos.longitude)[1], 2)
            }
        
        return {
            "datetime_utc": dt.isoformat(),
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "planets": planets_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating planetary positions: {str(e)}"
        )
