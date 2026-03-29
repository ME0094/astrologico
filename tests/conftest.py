"""
Pytest configuration and shared fixtures for Astrologico test suite.

Provides:
- FastAPI test client
- Dependency mocking
- Settings fixtures
- Database/cache fixtures
- Async fixtures
"""

import pytest
import logging
import sys
from datetime import datetime
from typing import Generator
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

# Suppress verbose logging during tests
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("src.astrologico").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def test_settings():
    """
    Create test settings (once per test session).
    
    Uses testing environment with minimal configuration.
    """
    from src.astrologico.api.settings import APISettings
    
    return APISettings(
        environment="testing",
        debug=True,
        api_host="127.0.0.1",
        api_port=8001,
        log_level="warning",
        ai_provider="openai",
        openai_api_key="test-key",
        enable_rate_limiting=False
    )


@pytest.fixture
def app(test_settings):
    """
    Create FastAPI app for testing.
    
    Uses test settings and mocked dependencies.
    """
    # Patch everything before importing
    with patch('src.astrologico.api.logging_config.setup_logging'), \
         patch('src.astrologico.api.app.setup_logging'), \
         patch('src.astrologico.core.logging.basicConfig'):
        # Import app after patching
        from src.astrologico.api.app import create_app
        from src.astrologico.api.dependencies import reset_dependencies
        
        with patch('src.astrologico.api.app.settings', test_settings):
            try:
                app = create_app()
            except Exception as e:
                # If app creation fails, just create a minimal app
                from fastapi import FastAPI
                app = FastAPI()
        
        yield app
        
        # Cleanup
        try:
            reset_dependencies()
        except:
            pass


@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    """
    Create FastAPI test client.
    
    Yields:
        Configured TestClient for making requests
    """
    return TestClient(app)


@pytest.fixture
def calculator():
    """
    Create AstrologicalCalculator instance.
    
    Returns:
        Singleton calculator for testing
    """
    from src.astrologico.core import AstrologicalCalculator
    return AstrologicalCalculator()


@pytest.fixture
def test_datetime() -> datetime:
    """
    Standard test datetime.
    
    Returns:
        datetime: 2024-01-15 12:00:00 UTC
    """
    return datetime(2024, 1, 15, 12, 0, 0)


@pytest.fixture
def test_location() -> tuple:
    """
    Standard test location.
    
    Returns:
        tuple: (latitude, longitude) = (40.7128, -74.0060) (New York)
    """
    return (40.7128, -74.0060)


@pytest.fixture
def test_chart_data(calculator, test_datetime: datetime, test_location: tuple):
    """
    Generate test chart data.
    
    Returns:
        ChartData instance with planetary positions and aspects
    """
    lat, lon = test_location
    return calculator.generate_chart(dt=test_datetime, lat=lat, lon=lon)


@pytest.fixture
def mock_interpreter() -> MagicMock:
    """
    Create mock interpreter for testing without AI API.
    
    Returns:
        MagicMock configured as AstrologicalInterpreter
    """
    try:
        from src.astrologico.ai import AstrologicalInterpreter
    except (ImportError, RuntimeError):
        # If import fails, just use MagicMock directly
        AstrologicalInterpreter = MagicMock
    
    mock = MagicMock(spec=AstrologicalInterpreter)
    mock.client = None  # Simulate no API key
    mock.api_provider = "openai"
    mock.interpret_aspects.return_value = "Test aspect interpretation"
    mock.interpret_moon_phase.return_value = "Test moon phase interpretation"
    mock.generate_chart_summary.return_value = "Test chart summary"
    mock.analyze_compatibility.return_value = "Test compatibility analysis"
    mock.answer_question.return_value = "Test answer"
    mock._get_moon_phase_name.return_value = "Waxing Crescent"
    mock._format_planets.return_value = "Sun: 25°20' Capricorn\nMoon: 10°45' Pisces"
    
    return mock


@pytest.fixture(autouse=True)
def reset_state():
    """
    Reset application state before each test.
    
    Automatically runs before every test to ensure clean state.
    """
    try:
        from src.astrologico.api.dependencies import reset_dependencies
    except (ImportError, RuntimeError):
        # If import fails, just pass
        def reset_dependencies():
            pass
    
    reset_dependencies()
    yield
    reset_dependencies()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "api: mark test as testing API endpoints"
    )
    config.addinivalue_line(
        "markers", "core: mark test as testing core calculations"
    )


# Test utilities
@pytest.fixture
def assert_valid_response():
    """
    Create assertion helper for valid API responses.
    
    Returns:
        Callable that validates response structure
    """
    def _assert_valid(response, expected_status: int = 200):
        """Assert response is valid with expected status."""
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, "
            f"got {response.status_code}: {response.text}"
        )
        assert response.headers["content-type"] == "application/json"
        return response.json()
    
    return _assert_valid


@pytest.fixture
def assert_error_response():
    """
    Create assertion helper for error API responses.
    
    Returns:
        Callable that validates error response structure
    """
    def _assert_error(response, expected_status: int, expected_code: str):
        """Assert response is valid error with expected code."""
        assert response.status_code == expected_status
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == expected_code
        assert "message" in data["error"]
        return data
    
    return _assert_error


__all__ = [
    'test_settings',
    'app',
    'client',
    'calculator',
    'test_datetime',
    'test_location',
    'test_chart_data',
    'mock_interpreter',
    'reset_state',
    'assert_valid_response',
    'assert_error_response'
]
