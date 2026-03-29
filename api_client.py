#!/usr/bin/env python3
"""
Client CLI for communicating with Astrologico AI API.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional

try:
    import requests
    from requests.exceptions import RequestException
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)


class AstrologicoAPIClient:
    """Client for Astrologico AI API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def check_health(self) -> dict:
        """Check API health."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e), "status": "unavailable"}
    
    def get_chart(self, date: str, lat: float, lon: float, 
                  include_interpretation: bool = True) -> dict:
        """Generate astrological chart."""
        url = f"{self.base_url}/api/v1/chart/quick"
        params = {
            "date": date,
            "lat": lat,
            "lon": lon,
            "json_output": not include_interpretation
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}
    
    def get_planets(self, date: str, lat: float = 0.0, lon: float = 0.0) -> dict:
        """Get planetary positions."""
        url = f"{self.base_url}/api/v1/planets"
        params = {"date": date, "lat": lat, "lon": lon}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}
    
    def get_aspects(self, date: str, lat: float = 0.0, lon: float = 0.0,
                    orb: float = 8.0) -> dict:
        """Calculate aspects."""
        url = f"{self.base_url}/api/v1/aspects"
        params = {"date": date, "lat": lat, "lon": lon, "orb": orb}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}
    
    def get_moon(self, date: str) -> dict:
        """Get moon phase."""
        url = f"{self.base_url}/api/v1/moon"
        params = {"date": date}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}
    
    def ask_question(self, question: str, date: Optional[str] = None,
                     lat: Optional[float] = None, lon: Optional[float] = None) -> dict:
        """Ask an astrological question."""
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
    
    def analyze_compatibility(self, date1: str, lat1: float, lon1: float,
                             date2: str, lat2: float, lon2: float) -> dict:
        """Analyze compatibility between two charts."""
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
    
    def get_status(self) -> dict:
        """Get API status."""
        url = f"{self.base_url}/api/v1/status"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {"error": str(e)}


def print_json(data: dict, pretty: bool = True):
    """Print JSON data."""
    if pretty:
        print(json.dumps(data, indent=2))
    else:
        print(json.dumps(data))


def main():
    """Main CLI entry."""
    parser = argparse.ArgumentParser(
        description='Astrologico AI API Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s chart --date "2026-03-29 12:00:00" --lat 40.7128 --lon -74.0060
  %(prog)s chart --date "2000-01-15 09:30:00" --lat 51.5074 --lon -0.1278
  %(prog)s ask "What does Venus in Libra mean?" --date "2000-01-15 09:30:00"
  %(prog)s compatibility --date1 "2000-01-15" --lat1 40.7 --lon1 -74 --date2 "1995-06-20" --lat2 40.7 --lon2 -74
  %(prog)s status
        '''
    )
    
    # Global options
    parser.add_argument('--url', default='http://localhost:8000',
                       help='API base URL (default: http://localhost:8000)')
    parser.add_argument('--json', action='store_true', help='Compact JSON output')
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Chart command
    chart_parser = subparsers.add_parser('chart', help='Get astrological chart')
    chart_parser.add_argument('--date', required=True, help='ISO datetime (YYYY-MM-DD HH:MM:SS)')
    chart_parser.add_argument('--lat', type=float, default=0.0, help='Latitude')
    chart_parser.add_argument('--lon', type=float, default=0.0, help='Longitude')
    chart_parser.add_argument('--no-interpret', action='store_true', help='Skip AI interpretation')
    
    # Planets command
    planets_parser = subparsers.add_parser('planets', help='Get planetary positions')
    planets_parser.add_argument('--date', required=True, help='ISO datetime')
    planets_parser.add_argument('--lat', type=float, default=0.0, help='Latitude')
    planets_parser.add_argument('--lon', type=float, default=0.0, help='Longitude')
    
    # Aspects command
    aspects_parser = subparsers.add_parser('aspects', help='Calculate aspects')
    aspects_parser.add_argument('--date', required=True, help='ISO datetime')
    aspects_parser.add_argument('--lat', type=float, default=0.0, help='Latitude')
    aspects_parser.add_argument('--lon', type=float, default=0.0, help='Longitude')
    aspects_parser.add_argument('--orb', type=float, default=8.0, help='Orb in degrees')
    
    # Moon command
    moon_parser = subparsers.add_parser('moon', help='Get moon phase')
    moon_parser.add_argument('--date', required=True, help='ISO datetime')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask astrological question')
    ask_parser.add_argument('question', help='Your question')
    ask_parser.add_argument('--date', help='Optional ISO datetime for context')
    ask_parser.add_argument('--lat', type=float, help='Optional latitude for context')
    ask_parser.add_argument('--lon', type=float, help='Optional longitude for context')
    
    # Compatibility command
    compat_parser = subparsers.add_parser('compatibility', help='Analyze compatibility')
    compat_parser.add_argument('--date1', required=True, help='Person 1 datetime')
    compat_parser.add_argument('--lat1', type=float, required=True, help='Person 1 latitude')
    compat_parser.add_argument('--lon1', type=float, required=True, help='Person 1 longitude')
    compat_parser.add_argument('--date2', required=True, help='Person 2 datetime')
    compat_parser.add_argument('--lat2', type=float, required=True, help='Person 2 latitude')
    compat_parser.add_argument('--lon2', type=float, required=True, help='Person 2 longitude')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check API status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = AstrologicoAPIClient(args.url)
    
    try:
        if args.command == 'chart':
            result = client.get_chart(args.date, args.lat, args.lon,
                                     include_interpretation=not args.no_interpret)
        
        elif args.command == 'planets':
            result = client.get_planets(args.date, args.lat, args.lon)
        
        elif args.command == 'aspects':
            result = client.get_aspects(args.date, args.lat, args.lon, args.orb)
        
        elif args.command == 'moon':
            result = client.get_moon(args.date)
        
        elif args.command == 'ask':
            result = client.ask_question(
                args.question,
                date=args.date,
                lat=args.lat,
                lon=args.lon
            )
        
        elif args.command == 'compatibility':
            result = client.analyze_compatibility(
                args.date1, args.lat1, args.lon1,
                args.date2, args.lat2, args.lon2
            )
        
        elif args.command == 'status':
            result = client.get_status()
        
        else:
            print("Unknown command")
            return 1
        
        print_json(result, pretty=not args.json)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main() or 0)
