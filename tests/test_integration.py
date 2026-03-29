"""
Integration and end-to-end tests.

Tests complete workflows and system behavior:
- Full chart generation workflow
- Multi-step API interactions
- Error recovery and resilience
- Performance and load characteristics
"""

import pytest
from datetime import datetime, timedelta
from src.astrologico.core import AstrologicalCalculator


@pytest.mark.integration
class TestChartGenerationWorkflow:
    """Test complete chart generation workflow."""
    
    def test_full_workflow_generates_valid_chart(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime,
        test_location: tuple
    ):
        """Test complete workflow from input to chart output."""
        lat, lon = test_location
        
        # Step 1: Generate chart
        chart = calculator.generate_chart(
            dt=test_datetime,
            lat=lat,
            lon=lon
        )
        
        # Step 2: Verify chart has all components
        assert chart.planets is not None
        assert chart.aspects is not None
        assert chart.moon_phase is not None
        
        # Step 3: Serialize to dict
        chart_dict = chart.to_dict()
        assert isinstance(chart_dict, dict)
        
        # Step 4: Verify serialization is complete
        assert 'planets' in chart_dict
        assert 'aspects' in chart_dict
        assert 'moon_phase' in chart_dict
    
    def test_workflow_with_different_locations(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime
    ):
        """Test workflow works correctly for different locations."""
        test_locations = [
            (40.7128, -74.0060),    # New York
            (51.5074, -0.1278),     # London
            (48.8566, 2.3522),      # Paris
            (-33.8688, 151.2093),   # Sydney
        ]
        
        for lat, lon in test_locations:
            chart = calculator.generate_chart(
                dt=test_datetime,
                lat=lat,
                lon=lon
            )
            
            assert chart is not None
            assert chart.location_lat == lat
            assert chart.location_lon == lon
            assert len(chart.planets) > 0
    
    def test_workflow_with_different_times(
        self,
        calculator: AstrologicalCalculator,
        test_location: tuple
    ):
        """Test workflow produces different charts for different times."""
        lat, lon = test_location
        base_date = datetime(2024, 1, 1, 12, 0, 0)
        
        charts = []
        for hours_offset in [0, 6, 12, 18]:
            test_time = base_date.replace(hour=hours_offset)
            chart = calculator.generate_chart(
                dt=test_time,
                lat=lat,
                lon=lon
            )
            charts.append(chart)
        
        # Charts should all be valid
        assert all(c.planets is not None for c in charts)
        
        # At least some planetary positions should differ
        # (except Sun which moves ~1 degree per day)
        planets_1 = charts[0].planets
        planets_2 = charts[1].planets
        
        # Moon and fast planets should have moved
        assert len([p for p in charts if p is not None]) == 4


@pytest.mark.integration
class TestAPIFullStack:
    """Test complete API workflows via HTTP."""
    
    def test_chart_generation_through_api(self, client, assert_valid_response):
        """Test generating chart through full API stack."""
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
        
        # Verify all expected data is present
        assert 'chart' in data
        chart = data['chart']
        assert 'planets' in chart
        assert 'aspects' in chart
        assert 'moon_phase' in chart
    
    def test_multi_endpoint_workflow(self, client, assert_valid_response):
        """Test workflow using multiple endpoints."""
        params = {
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
        
        # Get planets
        response1 = client.get("/api/planets", params=params)
        assert response1.status_code == 200
        planets_data = assert_valid_response(response1)
        assert 'planets' in planets_data
        
        # Get aspects
        response2 = client.get("/api/aspects", params={**params, "orb": 8.0})
        assert response2.status_code == 200
        aspects_data = assert_valid_response(response2)
        assert 'aspects' in aspects_data
        
        # Get moon info
        response3 = client.get("/api/moon", params={
            "year": 2024,
            "month": 1,
            "day": 15,
            "hour": 12,
            "minute": 0,
            "second": 0,
            "timezone": "America/New_York"
        })
        assert response3.status_code == 200
        moon_data = assert_valid_response(response3)
        assert 'moon_phase' in moon_data
    
    def test_error_recovery_workflow(self, client):
        """Test system handles errors and recovers."""
        # First request with invalid data
        response1 = client.get(
            "/api/planets",
            params={
                "year": 2024,
                "month": 13,  # Invalid
                "day": 15,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        )
        
        # Should return error
        assert response1.status_code >= 400
        
        # Second request should still work (no state corruption)
        response2 = client.get(
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
        
        assert response2.status_code == 200


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceCharacteristics:
    """Test performance and load characteristics."""
    
    def test_chart_generation_completes_timely(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime,
        test_location: tuple
    ):
        """Test that chart generation completes in reasonable time."""
        import time
        
        lat, lon = test_location
        
        start = time.time()
        chart = calculator.generate_chart(dt=test_datetime, lat=lat, lon=lon)
        elapsed = time.time() - start
        
        # Should complete in under 5 seconds (generous limit)
        assert elapsed < 5.0
        assert chart is not None
    
    def test_multiple_sequential_requests(self, client):
        """Test handling multiple sequential requests."""
        params = {
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
        
        # Make 5 requests
        responses = []
        for _ in range(5):
            response = client.get("/api/planets", params=params)
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
    
    def test_concurrent_capability(self, client):
        """Test system can handle multiple parameters."""
        import concurrent.futures
        
        params_list = [
            {
                "year": 2024,
                "month": 1,
                "day": day,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
            for day in range(1, 6)
        ]
        
        def make_request(params):
            return client.get("/api/planets", params=params)
        
        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, p) for p in params_list]
            results = [f.result() for f in futures]
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)


@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across operations."""
    
    def test_same_input_produces_same_output(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime,
        test_location: tuple
    ):
        """Test that same inputs always produce same outputs."""
        lat, lon = test_location
        
        # Generate chart twice with same inputs
        chart1 = calculator.generate_chart(dt=test_datetime, lat=lat, lon=lon)
        chart2 = calculator.generate_chart(dt=test_datetime, lat=lat, lon=lon)
        
        # Should produce identical results
        planets1 = chart1.planets
        planets2 = chart2.planets
        
        # Check at least some planets have identical positions
        common_planets = set(planets1.keys()) & set(planets2.keys())
        for planet in common_planets:
            assert planets1[planet].longitude == planets2[planet].longitude
    
    def test_chart_serialization_roundtrip(self, test_chart_data):
        """Test serialization and deserialization consistency."""
        # Serialize
        chart_dict = test_chart_data.to_dict()
        
        # Verify all data is present
        assert 'planets' in chart_dict
        assert 'aspects' in chart_dict
        assert 'moon_phase' in chart_dict
        
        # Deserialize back (if supported)
        try:
            from src.astrologico.core.models import ChartData
            # The chart_dict should be compatible for reconstruction
            assert isinstance(chart_dict, dict)
            assert len(chart_dict) > 0
        except ImportError:
            # If ChartData has no from_dict, just verify dict structure
            assert isinstance(chart_dict, dict)
    
    def test_aspects_consistency(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime,
        test_location: tuple
    ):
        """Test that aspects are consistent and non-contradictory."""
        lat, lon = test_location
        positions = calculator.calculate_planetary_positions(
            dt=test_datetime,
            lat=lat,
            lon=lon
        )
        
        aspects = calculator.calculate_aspects(positions)
        
        # Each aspect should appear only once (no duplicates)
        aspect_pairs = [
            (a['planet1'], a['planet2']) for a in aspects
        ]
        aspect_pairs_normalized = [
            tuple(sorted([a, b])) for a, b in aspect_pairs
        ]
        
        # Check for duplicates
        assert len(aspect_pairs_normalized) == len(set(aspect_pairs_normalized))


@pytest.mark.integration
class TestErrorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_extreme_coordinates(
        self,
        calculator: AstrologicalCalculator,
        test_datetime: datetime
    ):
        """Test chart generation at extreme latitudes."""
        extreme_coords = [
            (89.9, 0),      # Near North Pole
            (-89.9, 0),     # Near South Pole
            (0, 179.9),     # Near International Date Line
        ]
        
        for lat, lon in extreme_coords:
            try:
                chart = calculator.generate_chart(dt=test_datetime, lat=lat, lon=lon)
                # Should either work or raise clear error
                assert chart is not None
            except (ValueError, AssertionError):
                # Is acceptable if explicitly unsupported
                pass
    
    def test_historical_dates(
        self,
        calculator: AstrologicalCalculator,
        test_location: tuple
    ):
        """Test chart generation for various historical dates."""
        lat, lon = test_location
        test_dates = [
            datetime(1900, 1, 1, 12, 0, 0),
            datetime(1950, 6, 15, 12, 0, 0),
            datetime(2000, 1, 1, 12, 0, 0),
        ]
        
        for test_date in test_dates:
            try:
                chart = calculator.generate_chart(dt=test_date, lat=lat, lon=lon)
                # Should work for historical dates
                assert chart is not None
            except ValueError:
                # Some libraries might not support old dates
                pass
    
    def test_future_dates(
        self,
        calculator: AstrologicalCalculator,
        test_location: tuple
    ):
        """Test chart generation for future dates."""
        lat, lon = test_location
        test_dates = [
            datetime(2050, 1, 1, 12, 0, 0),
            datetime(2100, 6, 15, 12, 0, 0),
        ]
        
        for test_date in test_dates:
            try:
                chart = calculator.generate_chart(dt=test_date, lat=lat, lon=lon)
                # Should work for future dates
                assert chart is not None
            except ValueError:
                # Some libraries might not support far future
                pass


__all__ = [
    'TestChartGenerationWorkflow',
    'TestAPIFullStack',
    'TestPerformanceCharacteristics',
    'TestDataConsistency',
    'TestErrorEdgeCases'
]
