"""
Shared API utilities and helper functions.

Provides common validation, parsing, and conversion functions used across multiple routes.
"""

from datetime import datetime
from typing import Any, Dict, Optional, List
from fastapi import HTTPException
from astrologico.core import (
    validate_latitude as core_validate_latitude,
    validate_longitude as core_validate_longitude,
    ChartDict,
    ChartResponseDict,
    chart_dict_to_response_dict,
    InterpretationDict
)
from astrologico.api.models import DateTimeInput


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate latitude and longitude coordinates.
    
    Args:
        latitude: Latitude value (-90 to 90)
        longitude: Longitude value (-180 to 180)
    
    Returns:
        True if valid, False otherwise
    
    Raises:
        HTTPException: If validation fails
    """
    if not core_validate_latitude(latitude):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid latitude: {latitude}. Must be between -90 and 90."
        )
    if not core_validate_longitude(longitude):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid longitude: {longitude}. Must be between -180 and 180."
        )
    return True


def parse_datetime(datetime_input: DateTimeInput) -> datetime:
    """
    Parse datetime from input model.
    
    Handles both explicit datetime strings and special 'now' flag.
    
    Args:
        datetime_input: DateTimeInput model with datetime_str and use_now fields
    
    Returns:
        Parsed datetime.datetime object in UTC
    
    Raises:
        HTTPException: If datetime string is invalid or no datetime specified
    """
    if datetime_input.use_now:
        return datetime.utcnow()
    
    if datetime_input.datetime_str:
        try:
            # Support multiple datetime formats
            dt_str = datetime_input.datetime_str
            # Try ISO format first
            try:
                return datetime.fromisoformat(dt_str)
            except ValueError:
                # Try common alternative format: YYYY-MM-DD HH:MM:SS
                if " " in dt_str:
                    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                # Try ISO date format: YYYY-MM-DD
                else:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d")
                    return dt
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid datetime format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS) or 'now'. Error: {str(e)}"
            )
    
    raise HTTPException(
        status_code=400,
        detail="Specify datetime_str or set use_now=true"
    )


def format_chart_response(
    chart_dict: ChartDict,
    moon_phase_name: str,
    interpretation: Optional[InterpretationDict] = None
) -> ChartResponseDict:
    """
    Convert internal ChartDict to API response format.
    
    Args:
        chart_dict: Internal chart data structure
        moon_phase_name: Human-readable moon phase name (e.g., "Full Moon")
        interpretation: Optional AI interpretation results
    
    Returns:
        Formatted chart response dictionary
    """
    response = chart_dict_to_response_dict(
        chart_dict,
        moon_phase_name,
        interpretation
    )
    return response


def validate_and_parse_location(latitude: float, longitude: float) -> tuple:
    """
    Validate and return location coordinates.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
    
    Returns:
        Tuple of (latitude, longitude)
    
    Raises:
        HTTPException: If coordinates are invalid
    """
    validate_coordinates(latitude, longitude)
    return (latitude, longitude)


def standardize_response(
    success: bool,
    data: Any = None,
    error: Optional[str] = None,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized API response structure.
    
    Args:
        success: Whether request was successful
        data: Response data (if successful)
        error: Error message (if failed)
        message: Optional additional message
    
    Returns:
        Standardized response dictionary
    """
    response: Dict[str, Any] = {"success": success}
    
    if data is not None:
        response["data"] = data
    
    if error is not None:
        response["error"] = error
    
    if message is not None:
        response["message"] = message
    
    return response


__all__ = [
    'validate_coordinates',
    'parse_datetime',
    'format_chart_response',
    'validate_and_parse_location',
    'standardize_response'
]
