"""
HTTP client for communicating with Astrologico AI API.

Provides programmatic access to all API endpoints with error handling
and convenient methods for chart generation, analysis, and queries.
"""

from typing import Optional, Dict, Any
import sys

try:
    import requests
    from requests.exceptions import RequestException
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)


class AstrologicoAPIClient:
    """
    Client for Astrologico AI API.
    
    Provides convenient Python interface to all astrological API endpoints.
    
    Args:
        base_url: API base URL (default: http://localhost:8000)
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client.
        
        Args:
            base_url: API base URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def check_health(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Health status dictionary
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e), "status": "unavailable"}

    def get_chart(self,
                  date: str,
                  lat: float,
                  lon: float,
                  include_interpretation: bool = True) -> Dict[str, Any]:
        """
        Generate astrological chart.
        
        Args:
            date: ISO datetime string (YYYY-MM-DD HH:MM:SS)
            lat: Observer latitude
            lon: Observer longitude
            include_interpretation: Whether to include AI interpretation
        
        Returns:
            Chart data with planetary positions and aspects
        """
        url = f"{self.base_url}/api/v1/chart/quick"
        params = {
            "date": date,
            "lat": lat,
            "lon": lon,
            "no_interpretation": not include_interpretation
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}

    def get_planets(self,
                    date: str,
                    lat: float = 0.0,
                    lon: float = 0.0) -> Dict[str, Any]:
        """
        Get planetary positions.
        
        Args:
            date: ISO datetime string
            lat: Observer latitude
            lon: Observer longitude
        
        Returns:
            Planetary position data
        """
        url = f"{self.base_url}/api/v1/planets"
        params = {"date": date, "lat": lat, "lon": lon}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}

    def get_aspects(self,
                    date: str,
                    lat: float = 0.0,
                    lon: float = 0.0,
                    orb: float = 8.0) -> Dict[str, Any]:
        """
        Calculate planetary aspects.
        
        Args:
            date: ISO datetime string
            lat: Observer latitude
            lon: Observer longitude
            orb: Aspect orb in degrees
        
        Returns:
            Aspects data with angles and orbs
        """
        url = f"{self.base_url}/api/v1/aspects"
        params = {"date": date, "lat": lat, "lon": lon, "orb": orb}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}

    def get_moon(self, date: str) -> Dict[str, Any]:
        """
        Get moon phase information.
        
        Args:
            date: ISO datetime string
        
        Returns:
            Moon phase data with illumination
        """
        url = f"{self.base_url}/api/v1/moon"
        params = {"date": date}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}

    def ask_question(self,
                     question: str,
                     date: Optional[str] = None,
                     lat: Optional[float] = None,
                     lon: Optional[float] = None) -> Dict[str, Any]:
        """
        Ask an astrological question.
        
        Args:
            question: The question to ask
            date: Optional ISO datetime for chart context
            lat: Optional latitude for chart context
            lon: Optional longitude for chart context
        
        Returns:
            AI answer with optional chart context
        """
        url = f"{self.base_url}/api/v1/ask"
        payload = {"question": question}

        if date:
            payload["datetime"] = {"datetime_str": date, "use_now": False}
        if lat is not None and lon is not None:
            payload["location"] = {"latitude": lat, "longitude": lon}

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}

    def analyze_compatibility(self,
                             date1: str,
                             lat1: float,
                             lon1: float,
                             date2: str,
                             lat2: float,
                             lon2: float) -> Dict[str, Any]:
        """
        Analyze astrological compatibility between two people.
        
        Args:
            date1: Person 1 ISO datetime
            lat1: Person 1 latitude
            lon1: Person 1 longitude
            date2: Person 2 ISO datetime
            lat2: Person 2 latitude
            lon2: Person 2 longitude
        
        Returns:
            Compatibility analysis with both charts
        """
        url = f"{self.base_url}/api/v1/analysis/compatibility"
        payload = {
            "person1_datetime": {"datetime_str": date1, "use_now": False},
            "person1_location": {"latitude": lat1, "longitude": lon1},
            "person2_datetime": {"datetime_str": date2, "use_now": False},
            "person2_location": {"latitude": lat2, "longitude": lon2}
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}

    def analyze_transits(self,
                        natal_date: str,
                        natal_lat: float,
                        natal_lon: float,
                        transit_date: str) -> Dict[str, Any]:
        """
        Analyze transits to a natal chart.
        
        Args:
            natal_date: Natal ISO datetime
            natal_lat: Natal latitude
            natal_lon: Natal longitude
            transit_date: Transit ISO datetime
        
        Returns:
            Transit analysis with both charts
        """
        url = f"{self.base_url}/api/v1/analysis/transits"
        payload = {
            "natal_datetime": {"datetime_str": natal_date, "use_now": False},
            "natal_location": {"latitude": natal_lat, "longitude": natal_lon},
            "transit_datetime": {"datetime_str": transit_date, "use_now": False}
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """
        Get API status and available endpoints.
        
        Returns:
            API status information
        """
        url = f"{self.base_url}/api/v1/status"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
