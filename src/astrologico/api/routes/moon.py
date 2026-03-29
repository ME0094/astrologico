"""
Moon phase routes.

Provides endpoints for moon phase calculations and interpretation.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from astrologico.api.models import MoonResponse, MoonInterpretationResponse
from astrologico.api.dependencies import get_calculator, get_interpreter, verify_ai_api_key

router = APIRouter(prefix="/api/v1", tags=["moon"])


@router.get("/moon", response_model=MoonResponse)
async def get_moon(
    now: bool = Query(False, description="Use current UTC time"),
    date: Optional[str] = Query(None, description="ISO datetime string")
):
    """
    Get moon phase information.
    
    Args:
        now: Use current UTC time
        date: ISO datetime string (YYYY-MM-DD HH:MM:SS)
    
    Returns:
        Moon phase, name, and illumination percentage
    """
    calculator = get_calculator()
    interpreter = get_interpreter()
    
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
        
        # Calculate moon phase
        phase = calculator.calculate_moon_phase(dt)
        phase_name = interpreter._get_moon_phase_name(phase)
        
        return {
            "datetime_utc": dt.isoformat(),
            "phase": round(phase, 4),
            "phase_name": phase_name,
            "illumination": f"{phase * 100:.1f}%"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating moon phase: {str(e)}"
        )


@router.get("/interpret/moon", response_model=MoonInterpretationResponse)
async def interpret_moon(
    phase: float = Query(..., ge=0, le=1, description="Moon phase (0=new, 0.5=full)"),
    api_key: str = Depends(verify_ai_api_key)
):
    """
    Get AI interpretation of moon phase.
    
    Args:
        phase: Moon phase value from 0 to 1
            - 0.0 = New Moon
            - 0.25 = First Quarter
            - 0.5 = Full Moon
            - 0.75 = Last Quarter
    
    Returns:
        Moon phase name and AI interpretation
    
    Note:
        Requires AI provider API key to be configured
    """
    interpreter = get_interpreter()
    
    if not interpreter.client:
        raise HTTPException(
            status_code=503,
            detail="AI interpreter not available. Configure API key."
        )
    
    try:
        if not (0 <= phase <= 1):
            raise HTTPException(
                status_code=400,
                detail="Phase must be between 0 and 1"
            )
        
        phase_name = interpreter._get_moon_phase_name(phase)
        interpretation = interpreter.interpret_moon_phase(phase)
        
        return {
            "moon_phase": phase,
            "phase_name": phase_name,
            "interpretation": interpretation
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interpreting moon phase: {str(e)}"
        )
