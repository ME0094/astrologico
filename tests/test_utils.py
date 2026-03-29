"""
Tests for utility functions and helpers.

Tests shared utilities in the API package.
"""

import pytest
from datetime import datetime


@pytest.mark.unit
class TestCoordinateValidation:
    """Test validate_coordinates function."""
    
    def test_valid_coordinates(self, test_location):
        """Test validation of valid coordinates."""
        from src.astrologico.api.utils import validate_coordinates
        
        lat, lon = test_location
        result = validate_coordinates(lat, lon)
        assert result is True
    
    def test_coordinates_at_boundaries(self):
        """Test extreme but valid coordinates."""
        from src.astrologico.api.utils import validate_coordinates
        
        test_cases = [
            (90, 180),
            (-90, -180),
            (0, 0),
            (45, -120),
        ]
        
        for lat, lon in test_cases:
            result = validate_coordinates(lat, lon)
            assert result is True
    
    def test_invalid_latitude_too_high(self):
        """Test latitude > 90."""
        from src.astrologico.api.utils import validate_coordinates
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException):
            validate_coordinates(91, 0)
    
    def test_invalid_latitude_too_low(self):
        """Test latitude < -90."""
        from src.astrologico.api.utils import validate_coordinates
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException):
            validate_coordinates(-91, 0)
    
    def test_invalid_longitude_too_high(self):
        """Test longitude > 180."""
        from src.astrologico.api.utils import validate_coordinates
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException):
            validate_coordinates(0, 181)
    
    def test_invalid_longitude_too_low(self):
        """Test longitude < -180."""
        from src.astrologico.api.utils import validate_coordinates
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException):
            validate_coordinates(0, -181)
    
    @pytest.mark.parametrize("lat,lon", [
        (45.5, -122.7),
        (51.5, -0.1),
        (48.9, 2.3),
        (-33.9, 151.2),
        (35.7, 139.7),
    ])
    def test_real_world_coordinates(self, lat, lon):
        """Test validation with real-world coordinates."""
        from src.astrologico.api.utils import validate_coordinates
        
        result = validate_coordinates(lat, lon)
        assert result is True


@pytest.mark.unit
class TestUtilityFunctions:
    """Test general utility functions."""
    
    def test_validate_coordinates_with_floats(self):
        """Test coordinate validation with float values."""
        from src.astrologico.api.utils import validate_coordinates
        
        assert validate_coordinates(40.7128, -74.006) is True
    
    def test_validate_coordinates_with_ints(self):
        """Test coordinate validation with integer values."""
        from src.astrologico.api.utils import validate_coordinates
        
        assert validate_coordinates(40, -74) is True
    
    def test_validate_coordinates_returns_boolean(self):
        """Test that validation returns boolean."""
        from src.astrologico.api.utils import validate_coordinates
        
        result = validate_coordinates(40.0, -74.0)
        assert isinstance(result, bool)
        assert result is True


__all__ = [
    'TestCoordinateValidation',
    'TestUtilityFunctions',
]
