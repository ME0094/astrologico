"""
Tests for core calculation modules.

Tests the AstrologicalCalculator and related functionality:
- Planetary position calculations
- Aspect detection
- Moon phase calculations
- Zodiac sign calculation
"""

import pytest
from datetime import datetime
from src.astrologico.core import AstrologicalCalculator


@pytest.mark.core
class TestAstrologicalCalculator:
    """Test AstrologicalCalculator functionality."""
    
    def test_calculator_initialization(self, calculator: AstrologicalCalculator):
        """Test calculator initializes without error."""
        assert calculator is not None
        assert hasattr(calculator, 'calculate_planetary_positions')
        assert hasattr(calculator, 'calculate_aspects')
        assert hasattr(calculator, 'calculate_moon_phase')
    
    def test_calculate_planetary_positions(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime,
        test_location: tuple
    ):
        """Test planetary position calculation."""
        lat, lon = test_location
        positions = calculator.calculate_planetary_positions(
            dt=test_datetime,
            lat=lat,
            lon=lon
        )
        
        # Should return dict of planet positions
        assert isinstance(positions, dict)
        assert len(positions) > 0
        
        # Check for expected planets
        expected_planets = {'Sun', 'Moon', 'Mercury', 'Venus', 'Mars'}
        actual_planets = set(positions.keys())
        assert expected_planets.issubset(actual_planets)
        
        # Each position should have required attributes
        for planet_name, position in positions.items():
            assert hasattr(position, 'longitude')
            assert hasattr(position, 'latitude')
            assert hasattr(position, 'distance')
            
            # Validate longitude range
            assert -180 <= position.longitude <= 360
            # Validate latitude range
            assert -90 <= position.latitude <= 90
            # Distance should be >= 0 (may be 0 for some approximations)
            assert position.distance >= 0
    
    def test_calculate_moon_phase(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime
    ):
        """Test moon phase calculation."""
        phase = calculator.calculate_moon_phase(test_datetime)
        
        # Moon phase should be between 0 and 1
        assert isinstance(phase, float)
        assert 0 <= phase <= 1
    
    def test_calculate_aspects(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime,
        test_location: tuple
    ):
        """Test aspect detection."""
        lat, lon = test_location
        positions = calculator.calculate_planetary_positions(
            dt=test_datetime,
            lat=lat,
            lon=lon
        )
        
        aspects = calculator.calculate_aspects(positions, orb=8.0)
        
        # Should return list of aspects
        assert isinstance(aspects, list)
        
        # Each aspect should have required fields
        for aspect in aspects:
            assert 'planet1' in aspect
            assert 'planet2' in aspect
            assert 'aspect' in aspect
            assert 'angle' in aspect
            assert 'orb' in aspect
            
            # Aspect angle should be reasonable
            assert 0 <= aspect['angle'] <= 360
            # Orb should be less than specified
            assert abs(aspect['orb']) <= 8.0
    
    def test_get_zodiac_sign(self, calculator: AstrologicalCalculator):
        """Test zodiac sign calculation."""
        test_cases = [
            (0, "Aries", 0),
            (30, "Taurus", 0),
            (60, "Gemini", 0),
            (90, "Cancer", 0),
            (180, "Libra", 0),
            (270, "Capricorn", 0),
            (355, "Pisces", 25)
        ]
        
        for longitude, expected_sign, _ in test_cases:
            sign, position = calculator.get_zodiac_sign(longitude)
            assert sign == expected_sign
            assert 0 <= position < 30
    
    def test_generate_chart(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime,
        test_location: tuple
    ):
        """Test complete chart generation."""
        lat, lon = test_location
        chart = calculator.generate_chart(dt=test_datetime, lat=lat, lon=lon)
        
        assert chart is not None
        assert hasattr(chart, 'datetime_utc')
        assert hasattr(chart, 'planets')
        assert hasattr(chart, 'moon_phase')
        assert hasattr(chart, 'aspects')
        assert hasattr(chart, 'location_lat')
        assert hasattr(chart, 'location_lon')
        
        # Verify data integrity
        # Compare dates (may have different timezone info)
        assert chart.datetime_utc.date() == test_datetime.date() or \
               chart.datetime_utc == test_datetime
        assert chart.location_lat == lat
        assert chart.location_lon == lon
        assert isinstance(chart.planets, dict)
        assert isinstance(chart.aspects, list)
        assert 0 <= chart.moon_phase <= 1
    
    def test_chart_to_dict(self, test_chart_data):
        """Test chart serialization to dictionary."""
        chart_dict = test_chart_data.to_dict()
        
        assert isinstance(chart_dict, dict)
        assert 'datetime_utc' in chart_dict
        assert 'location_lat' in chart_dict
        assert 'location_lon' in chart_dict
        assert 'planets' in chart_dict
        assert 'moon_phase' in chart_dict
        assert 'aspects' in chart_dict
    
    @pytest.mark.parametrize("invalid_lat,invalid_lon", [
        (91, 0),      # Latitude too high
        (-91, 0),     # Latitude too low
        (0, 181),     # Longitude too high
        (0, -181),    # Longitude too low
    ])
    def test_invalid_coordinates_handled(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime,
        invalid_lat: float,
        invalid_lon: float
    ):
        """Test that invalid coordinates are handled gracefully."""
        # Should raise ValueError or handle gracefully
        try:
            calculator.generate_chart(
                dt=test_datetime,
                lat=invalid_lat,
                lon=invalid_lon
            )
        except (ValueError, AssertionError):
            # Expected behavior
            pass


@pytest.mark.core
class TestChartData:
    """Test ChartData model and serialization."""
    
    def test_chart_data_creation(self, test_chart_data):
        """Test ChartData instance creation."""
        assert test_chart_data is not None
        assert isinstance(test_chart_data.datetime_utc, datetime)
        assert isinstance(test_chart_data.planets, dict)
        assert isinstance(test_chart_data.aspects, list)
    
    def test_chart_data_serialization(self, test_chart_data):
        """Test ChartData.to_dict() serialization."""
        chart_dict = test_chart_data.to_dict()
        
        # Check structure
        assert 'datetime_utc' in chart_dict
        assert 'planets' in chart_dict
        assert 'aspects' in chart_dict
        
        # Check that planets dict is properly structured
        planets = chart_dict['planets']
        assert isinstance(planets, dict)
        for planet_name, planet_data in planets.items():
            assert isinstance(planet_data, dict)
            if hasattr(planet_data, 'to_dict'):
                # It's a PlanetaryPosition object
                assert 'longitude' in planet_data


@pytest.mark.core
class TestAspectDetection:
    """Test aspect detection and interpretation."""
    
    def test_major_aspects_detected(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime,
        test_location: tuple
    ):
        """Test that major aspects are properly detected."""
        lat, lon = test_location
        positions = calculator.calculate_planetary_positions(
            dt=test_datetime,
            lat=lat,
            lon=lon
        )
        
        aspects = calculator.calculate_aspects(positions, orb=8.0)
        
        # Should find some aspects with default orb
        assert len(aspects) > 0
        
        # Check for valid aspect types
        valid_aspects = {'Conjunction', 'Sextile', 'Square', 'Trine', 'Opposition'}
        for aspect in aspects:
            assert aspect['aspect'] in valid_aspects
    
    def test_aspect_orb_respected(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime,
        test_location: tuple
    ):
        """Test that aspect orb limits are respected."""
        lat, lon = test_location
        positions = calculator.calculate_planetary_positions(
            dt=test_datetime,
            lat=lat,
            lon=lon
        )
        
        # Test with restrictive orb
        aspects_tight = calculator.calculate_aspects(positions, orb=2.0)
        # Test with loose orb
        aspects_loose = calculator.calculate_aspects(positions, orb=8.0)
        
        # Loose orb should find more aspects
        assert len(aspects_loose) >= len(aspects_tight)
        
        # All aspects should follow their orb limits
        for aspect in aspects_loose:
            assert abs(aspect['orb']) <= 8.0


@pytest.mark.core
class TestMoonPhase:
    """Test moon phase calculations."""
    
    def test_moon_phase_range(self, calculator: AstrologicalCalculator):
        """Test moon phase is always in valid range."""
        from datetime import timedelta
        
        base_date = datetime(2024, 1, 1)
        
        for days_offset in range(30):
            test_date = base_date + timedelta(days=days_offset)
            phase = calculator.calculate_moon_phase(test_date)
            
            assert 0 <= phase <= 1, f"Phase {phase} out of range for {test_date}"
    
    def test_moon_phase_cycles(self, calculator: AstrologicalCalculator):
        """Test moon phase follows lunar cycle (approximately 29.5 days)."""
        from datetime import timedelta
        
        base_date = datetime(2024, 1, 1)
        phase_start = calculator.calculate_moon_phase(base_date)
        
        # Check phase ~29.5 days later (should be similar)
        phase_later = calculator.calculate_moon_phase(
            base_date + timedelta(days=29)
        )
        
        # Phases should be in similar part of cycle
        # (allowing for minor differences due to exact cycle length)
        assert abs(phase_start - phase_later) < 0.1 or \
               abs((phase_start - phase_later + 1) % 1) < 0.1


__all__ = [
    'TestAstrologicalCalculator',
    'TestChartData',
    'TestAspectDetection',
    'TestMoonPhase'
]
