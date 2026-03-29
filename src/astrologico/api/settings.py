"""
API configuration using Pydantic Settings.

Loads configuration from environment variables with type validation and defaults.
Supports multiple environments (development, testing, production) with appropriate defaults.
"""

from typing import List, Literal
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class APISettings(BaseSettings):
    """API configuration settings."""

    # Environment
    environment: Literal["development", "testing", "production"] = Field(
        default="development",
        description="Deployment environment"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    # API Information
    api_title: str = Field(
        default="Astrologico AI API",
        description="API title for documentation"
    )
    api_description: str = Field(
        default="Professional astrological calculation and AI interpretation service",
        description="API description for documentation"
    )
    api_version: str = Field(
        default="2.0.0",
        description="API version"
    )

    # Server Configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="Server host address"
    )
    api_port: int = Field(
        default=8000,
        description="Server port"
    )

    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )

    # AI Configuration
    ai_provider: Literal["openai", "anthropic"] = Field(
        default="openai",
        description="AI API provider (openai or anthropic)"
    )
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key"
    )
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key"
    )
    ai_timeout: int = Field(
        default=30,
        description="AI API request timeout in seconds"
    )

    # Logging Configuration
    log_level: Literal["debug", "info", "warning", "error", "critical"] = Field(
        default="info",
        description="Logging level"
    )

    # Request Configuration
    request_timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    max_request_size: int = Field(
        default=1024 * 1024,  # 1MB
        description="Maximum request body size in bytes"
    )

    # Rate Limiting (optional)
    enable_rate_limiting: bool = Field(
        default=False,
        description="Enable rate limiting"
    )
    rate_limit_requests: int = Field(
        default=100,
        description="Requests allowed per rate_limit_period"
    )
    rate_limit_period: int = Field(
        default=60,
        description="Rate limit period in seconds"
    )

    @validator('ai_provider')
    def validate_ai_provider(cls, v: str) -> str:
        """Validate AI provider is one of supported values."""
        if v not in ["openai", "anthropic"]:
            raise ValueError("ai_provider must be 'openai' or 'anthropic'")
        return v

    @validator('api_port')
    def validate_api_port(cls, v: int) -> int:
        """Validate API port is in valid range."""
        if not (1 <= v <= 65535):
            raise ValueError("api_port must be between 1 and 65535")
        return v

    @validator('allowed_origins')
    def validate_origins(cls, v: List[str]) -> List[str]:
        """Validate CORS origins are not empty."""
        if not v and cls.environment == "production":
            raise ValueError("allowed_origins cannot be empty in production")
        return v

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Global settings instance
settings = APISettings()
