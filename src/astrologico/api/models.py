"""
Pydantic models for API requests and responses.

Defines the request/response schemas for all API endpoints.
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


# ============= Input Models =============

class LocationInput(BaseModel):
    """Location coordinates input."""
    latitude: float = Field(..., description="Location latitude (-90 to 90)")
    longitude: float = Field(..., description="Location longitude (-180 to 180)")
    name: Optional[str] = Field(None, description="Location name")


class DateTimeInput(BaseModel):
    """DateTime specification input."""
    datetime_str: Optional[str] = Field(None, description="ISO format datetime: YYYY-MM-DD HH:MM:SS")
    use_now: bool = Field(False, description="Use current UTC time if true")


class ChartRequest(BaseModel):
    """Request for astrological chart generation."""
    datetime: DateTimeInput = Field(..., description="DateTime for calculation")
    location: LocationInput = Field(..., description="Observer location")
    include_interpretation: bool = Field(True, description="Include AI interpretation")


class CompatibilityRequest(BaseModel):
    """Request for compatibility analysis."""
    person1_datetime: DateTimeInput = Field(..., description="First person datetime")
    person1_location: LocationInput = Field(..., description="First person location")
    person2_datetime: DateTimeInput = Field(..., description="Second person datetime")
    person2_location: LocationInput = Field(..., description="Second person location")


class TransitRequest(BaseModel):
    """Request for transit analysis."""
    natal_datetime: DateTimeInput = Field(..., description="Natal chart datetime")
    natal_location: LocationInput = Field(..., description="Natal location")
    transit_datetime: DateTimeInput = Field(..., description="Transit datetime")


class QuestionRequest(BaseModel):
    """Request for astrological Q&A."""
    question: str = Field(..., description="Astrological question")
    datetime: Optional[DateTimeInput] = Field(None, description="Optional chart datetime for context")
    location: Optional[LocationInput] = Field(None, description="Optional location for context")


# ============= Response Models =============

class PlanetaryData(BaseModel):
    """Planetary position data."""
    longitude: float = Field(..., description="Ecliptic longitude (degrees)")
    latitude: float = Field(..., description="Ecliptic latitude (degrees)")
    distance_au: float = Field(..., description="Distance from Sun (AU)")
    right_ascension: float = Field(..., description="Right ascension (hours)")
    declination: float = Field(..., description="Declination (degrees)")
    zodiac_sign: str = Field(..., description="Zodiac sign")
    sign_position: float = Field(..., description="Position in sign (0-30 degrees)")


class AspectData(BaseModel):
    """Aspect information."""
    planet1: str = Field(..., description="First planet name")
    planet2: str = Field(..., description="Second planet name")
    aspect: str = Field(..., description="Aspect type (Conjunction, Sextile, etc)")
    angle: float = Field(..., description="Actual angle between planets")
    aspect_angle: int = Field(..., description="Expected aspect angle")
    orb: float = Field(..., description="Orb (difference from exact aspect)")


class LocationData(BaseModel):
    """Location information."""
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")


class ChartResponse(BaseModel):
    """Complete astrological chart response."""
    datetime_utc: str = Field(..., description="UTC datetime")
    location: LocationData = Field(..., description="Observer location")
    planets: Dict[str, PlanetaryData] = Field(..., description="Planetary positions")
    moon_phase: float = Field(..., description="Moon phase (0-1)")
    moon_phase_name: str = Field(..., description="Moon phase name")
    aspects: List[AspectData] = Field(..., description="Planetary aspects")
    interpretation: Optional[Dict[str, str]] = Field(None, description="AI interpretation if requested")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status")
    calculator: str = Field(..., description="Calculator status")
    interpreter: str = Field(..., description="Interpreter status")


class StatusResponse(BaseModel):
    """API status response."""
    api_version: str = Field(..., description="API version")
    calculator_status: str = Field(..., description="Calculator status")
    interpreter_status: str = Field(..., description="Interpreter status")
    interpreter_provider: str = Field(..., description="AI provider (openai/anthropic)")
    ai_features_enabled: bool = Field(..., description="Whether AI features are enabled")
    endpoints: Dict[str, str] = Field(..., description="Available endpoints")


class MoonResponse(BaseModel):
    """Moon phase response."""
    datetime_utc: str = Field(..., description="UTC datetime")
    phase: float = Field(..., description="Moon phase (0-1)")
    phase_name: str = Field(..., description="Phase name")
    illumination: str = Field(..., description="Illumination percentage")


class PlanetsResponse(BaseModel):
    """Planetary positions response."""
    datetime_utc: str = Field(..., description="UTC datetime")
    location: LocationData = Field(..., description="Observer location")
    planets: Dict[str, Any] = Field(..., description="Planetary positions")


class AspectsResponse(BaseModel):
    """Aspects response."""
    datetime_utc: str = Field(..., description="UTC datetime")
    orb: float = Field(..., description="Orb used")
    aspects_count: int = Field(..., description="Number of aspects found")
    aspects: List[AspectData] = Field(..., description="List of aspects")


class AspectsInterpretationResponse(BaseModel):
    """Aspects interpretation response."""
    aspects: List[AspectData] = Field(..., description="Aspects analyzed")
    interpretation: str = Field(..., description="AI interpretation")


class MoonInterpretationResponse(BaseModel):
    """Moon interpretation response."""
    moon_phase: float = Field(..., description="Moon phase")
    phase_name: str = Field(..., description="Phase name")
    interpretation: str = Field(..., description="AI interpretation")


class CompatibilityResponse(BaseModel):
    """Compatibility analysis response."""
    person1_chart: ChartResponse = Field(..., description="First person's chart")
    person2_chart: ChartResponse = Field(..., description="Second person's chart")
    compatibility_analysis: str = Field(..., description="AI compatibility analysis")


class TransitsResponse(BaseModel):
    """Transits analysis response."""
    natal_chart: ChartResponse = Field(..., description="Natal chart")
    transit_chart: ChartResponse = Field(..., description="Transit chart")
    transit_analysis: str = Field(..., description="AI transit analysis")


class QuestionResponse(BaseModel):
    """Q&A response."""
    question: str = Field(..., description="The question asked")
    answer: str = Field(..., description="AI answer")
    chart_context: Optional[ChartResponse] = Field(None, description="Chart context if provided")
