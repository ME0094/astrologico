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

    # Rate Limiting
    enable_rate_limiting: bool = Field(
        default=True,
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

    # Authentication & Security
    require_api_key: bool = Field(
        default=False,
        description="Require API key for all requests (especially for AI endpoints)"
    )
    api_key_header: str = Field(
        default="X-API-Key",
        description="Header name for API key authentication"
    )
    api_key: str = Field(
        default="",
        description="API key for securing endpoints (empty = disabled)"
    )
    require_api_key_for_ai: bool = Field(
        default=True,
        description="Require API key specifically for AI/LLM endpoints"
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

    @validator('api_host')
    def validate_host(cls, v: str, values) -> str:
        """
        Validate API host binding.
        
        In production, strongly recommend localhost or specific IPs.
        0.0.0.0 is allowed but should be behind a reverse proxy.
        """
        environment = values.get('environment', 'development')
        if environment == "production" and v == "0.0.0.0":
            import warnings
            warnings.warn(
                "SECURITY WARNING: API.host=0.0.0.0 in production. "
                "This is dangerous without a reverse proxy. "
                "Use 127.0.0.1 or a specific IP.",
                SecurityWarning
            )
        return v

    @validator('allowed_origins')
    def validate_origins(cls, v: List[str], values) -> List[str]:
        """
        Validate CORS origins are secure.
        
        - Cannot be empty in production
        - Wildcard "*" cannot be used with allow_credentials=True
        - HTTPS required in production (unless localhost/127.0.0.1)
        """
        environment = values.get('environment', 'development')
        allow_credentials = values.get('allow_credentials', True)
        
        if not v and environment == "production":
            raise ValueError("allowed_origins cannot be empty in production")
        
        # Check for dangerous wildcard configuration
        if "*" in v and allow_credentials:
            raise ValueError(
                "SECURITY ERROR: Cannot use wildcard '*' in CORS origins "
                "with allow_credentials=True. This is a security vulnerability. "
                "Specify explicit origins instead."
            )
        
        # In production, require HTTPS for security
        if environment == "production":
            for origin in v:
                if not origin.startswith(("http://localhost", "http://127.0.0.1", "https://")):
                    import warnings
                    warnings.warn(
                        f"SECURITY WARNING: HTTP origin in production: {origin}. "
                        "HTTPS is recommended for production deployments.",
                        SecurityWarning
                    )
        
        return v

    def requires_api_key_for_ai(self) -> bool:
        """Check if API key is required for AI/LLM endpoints."""
        return self.require_api_key_for_ai or self.require_api_key

    def is_api_key_valid(self, key: str) -> bool:
        """Verify if provided API key matches configured key."""
        if not self.api_key:
            return False
        # Use constant-time comparison to prevent timing attacks
        import hmac
        return hmac.compare_digest(key, self.api_key)

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
