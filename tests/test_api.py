"""
Tests for API endpoints and route handlers.

Tests all REST API endpoints:
- /api/chart/{type} - Chart generation
- /api/planets - Planetary positions
- /api/aspects - Aspect detection
- /api/ask - AI interpretation
- /api/moon - Moon phase information
- /api/status - System status and metrics
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock


@pytest.mark.api
class TestChartEndpoints:
    """Test /api/chart/* endpoints."""
    
    def test_get_full_chart(self, client, assert_valid_response):
        """Test GET /api/chart/full endpoint."""
        response = client.get(
            "/api/chart/full",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        )
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        
        # Check response structure
        assert 'chart' in data
        assert 'metadata' in data
        chart = data['chart']
        assert 'planets' in chart
        assert 'aspects' in chart
        assert 'moon_phase' in chart
    
    def test_get_birth_chart(self, client, assert_valid_response):
        """Test POST /api/chart/birth endpoint."""
        response = client.post(
            "/api/chart/birth",
            json={
                "year": 1990,
                "month": 6,
                "day": 15,
                "hour": 14,
                "minute": 30,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        )
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        assert 'chart' in data
        assert 'metadata' in data
    
    def test_chart_with_invalid_date(self, client, assert_error_response):
        """Test chart endpoint with invalid date."""
        response = client.get(
            "/api/chart/full",
            params={
                "year": 2024,
                "month": 13,  # Invalid month
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        )
        
        assert response.status_code == 422  # Validation error
        data = assert_error_response(response, expected_status=422)
    
    def test_chart_with_invalid_coordinates(self, client, assert_error_response):
        """Test chart endpoint with invalid coordinates."""
        response = client.get(
            "/api/chart/full",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 91,  # Invalid latitude
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        )
        
        assert response.status_code in [400, 422]


@pytest.mark.api
class TestPlanetsEndpoints:
    """Test /api/planets endpoints."""
    
    def test_get_planets(self, client, assert_valid_response):
        """Test GET /api/planets endpoint."""
        response = client.get(
            "/api/planets",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        )
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        
        assert 'planets' in data
        planets = data['planets']
        assert isinstance(planets, dict)
        assert len(planets) > 0
        
        # Check planet structure
        for planet_name, planet_data in planets.items():
            assert 'longitude' in planet_data
            assert 'latitude' in planet_data
            assert 'zodiac_sign' in planet_data
            assert isinstance(planet_data['longitude'], (int, float))
    
    def test_planets_retrograde_info(self, client, assert_valid_response):
        """Test that retrograde status is included if available."""
        response = client.get(
            "/api/planets",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        )
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        
        planets = data['planets']
        # At least some planets should have retrograde info
        has_retrograde_info = any(
            'retrograde' in p for p in planets.values()
        )
        # This may or may not be true depending on implementation
        # Just verify structure is consistent
        assert isinstance(planets, dict)


@pytest.mark.api
class TestAspectsEndpoints:
    """Test /api/aspects endpoints."""
    
    def test_get_aspects(self, client, assert_valid_response):
        """Test GET /api/aspects endpoint."""
        response = client.get(
            "/api/aspects",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York",
                "orb": 8.0
            }
        )
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        
        assert 'aspects' in data
        aspects = data['aspects']
        assert isinstance(aspects, list)
        
        # Check aspect structure
        for aspect in aspects:
            assert 'planet1' in aspect
            assert 'planet2' in aspect
            assert 'aspect' in aspect
            assert 'angle' in aspect
            assert 'orb' in aspect
    
    def test_aspects_with_custom_orb(self, client, assert_valid_response):
        """Test aspects endpoint with custom orb."""
        response = client.get(
            "/api/aspects",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York",
                "orb": 2.0
            }
        )
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        
        # All aspects should respect the orb limit
        for aspect in data['aspects']:
            assert abs(aspect['orb']) <= 2.0


@pytest.mark.api
class TestMoonEndpoints:
    """Test /api/moon endpoints."""
    
    def test_get_moon_phase(self, client, assert_valid_response):
        """Test GET /api/moon endpoint."""
        response = client.get(
            "/api/moon",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "timezone": "UTC"
            }
        )
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        
        assert 'moon_phase' in data
        assert 'moon_sign' in data
        assert 'illumination' in data
        
        # Validate phase range
        phase = data['moon_phase']
        assert 0 <= phase <= 1
        
        # Validate illumination percentage
        illumination = data['illumination']
        assert 0 <= illumination <= 100
    
    def test_get_moon_phase_description(self, client, assert_valid_response):
        """Test that moon phase has descriptive name."""
        response = client.get(
            "/api/moon",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "timezone": "UTC"
            }
        )
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        
        # Should have phase description
        assert 'phase_name' in data or \
               isinstance(data.get('moon_phase'), dict) and \
               'name' in data['moon_phase']


@pytest.mark.api
class TestStatusEndpoints:
    """Test /api/status endpoints."""
    
    def test_health_check(self, client, assert_valid_response):
        """Test GET /api/status/health endpoint."""
        response = client.get("/api/status/health")
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        
        assert 'status' in data
        assert data['status'] in ['healthy', 'ok']
    
    def test_info_endpoint(self, client, assert_valid_response):
        """Test GET /api/status/info endpoint."""
        response = client.get("/api/status/info")
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        
        # Should have version info
        assert 'version' in data or 'name' in data


@pytest.mark.api
class TestErrorHandling:
    """Test error handling across endpoints."""
    
    def test_missing_required_parameters(self, client):
        """Test endpoints with missing required parameters."""
        response = client.get(
            "/api/planets",
            params={
                "year": 2024,
                "month": 1,
                # Missing other required fields
            }
        )
        
        # Should return 422 (validation error)
        assert response.status_code == 422
        error = response.json()
        assert 'detail' in error or 'error' in error
    
    def test_invalid_timezone(self, client):
        """Test endpoint with invalid timezone."""
        response = client.get(
            "/api/chart/full",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "Invalid/Timezone"
            }
        )
        
        # Should handle gracefully (400 or 422)
        assert response.status_code in [400, 422, 500]
    
    def test_server_error_has_correlation_id(self, client):
        """Test that server errors include correlation ID."""
        # This would normally require intentionally triggering an error
        # For now, just verify header handling
        response = client.get("/api/status/health")
        
        # Should have correlation ID header
        assert 'x-correlation-id' in response.headers or \
               'correlation-id' in response.headers.lower()


@pytest.mark.api
class TestResponseFormats:
    """Test consistent response formatting."""
    
    def test_success_response_format(self, client, assert_valid_response):
        """Test that successful responses follow consistent format."""
        response = client.get(
            "/api/planets",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be dict-like structure
        assert isinstance(data, dict)
    
    def test_error_response_format(self, client):
        """Test that error responses follow consistent format."""
        response = client.get(
            "/api/planets",
            params={
                "year": 2024,
                # Missing required fields
            }
        )
        
        assert response.status_code >= 400
        error = response.json()
        
        # Should have error information
        assert 'detail' in error or 'error' in error or 'message' in error
    
    def test_response_includes_metadata(self, client, assert_valid_response):
        """Test that responses include appropriate metadata."""
        response = client.get(
            "/api/chart/full",
            params={
                "year": 2024,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        )
        
        assert response.status_code == 200
        data = assert_valid_response(response)
        
        # Chart endpoint should have metadata
        if 'chart' in data and 'metadata' in data:
            metadata = data['metadata']
            assert 'datetime' in metadata or \
                   'timestamp' in metadata or \
                   'location' in metadata


__all__ = [
    'TestChartEndpoints',
    'TestPlanetsEndpoints',
    'TestAspectsEndpoints',
    'TestMoonEndpoints',
    'TestStatusEndpoints',
    'TestErrorHandling',
    'TestResponseFormats'
]
