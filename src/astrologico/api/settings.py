"""
API configuration using Pydantic Settings.

Loads configuration from environment variables with type validation and defaults.
"""

from typing import List
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """API configuration settings."""

    # API Information
    api_title: str = "Astrologico AI API"
    api_description: str = "Professional astrological calculation and AI interpretation service"
    api_version: str = "2.0.0"

    # Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS Configuration
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # AI Configuration
    ai_provider: str = "openai"  # openai or anthropic
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Logging Configuration
    log_level: str = "info"

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = APISettings()
