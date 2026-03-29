"""
Logging configuration for Astrologico API.

Provides structured logging setup with environment-specific configurations,
request correlation tracking, and performance monitoring.
"""

import logging
import logging.config
import sys
from typing import Dict, Any
from astrologico.api.settings import settings


def get_log_config() -> Dict[str, Any]:
    """
    Get logging configuration dictionary for Python's logging module.
    
    Returns:
        Dictionary suitable for logging.config.dictConfig()
    """
    log_level = settings.log_level.upper()
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "[%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(timestamp)s %(level)s %(name)s %(message)s"
            },
            "uvicorn_default": {
                "format": "%(asctime)s - %(levelname)s - %(message)s"
            },
            "uvicorn_access": {
                "format": "%(asctime)s - %(client_addr)s - \"%(request_line)s\" - %(status_code)s"
            }
        },
        "handlers": {
            "default": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "detailed": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/astrologico.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "detailed"
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/astrologico_error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "formatter": "detailed"
            }
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False
            },
            "src.astrologico": {
                "handlers": ["detailed", "file", "error_file"],
                "level": log_level,
                "propagate": True
            },
            "src.astrologico.api": {
                "handlers": ["detailed", "file", "error_file"],
                "level": log_level,
                "propagate": False
            },
            "src.astrologico.core": {
                "handlers": ["detailed", "file"],
                "level": log_level,
                "propagate": False
            },
            "src.astrologico.ai": {
                "handlers": ["detailed", "file"],
                "level": log_level,
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["default"]
        }
    }
    
    # In production, use more detailed logging
    if settings.is_production():
        config["loggers"]["src.astrologico"]["level"] = "INFO"
        # Remove file handlers in some production setups if using external logging
    
    # In development, use debug logging
    if settings.is_development():
        config["loggers"]["src.astrologico"]["level"] = "DEBUG"
    
    return config


def setup_logging() -> None:
    """
    Configure Python's logging system for Astrologico.
    
    Should be called early in application startup.
    """
    import os
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Apply configuration
    config = get_log_config()
    logging.config.dictConfig(config)
    
    # Get logger and log startup
    logger = logging.getLogger("src.astrologico")
    logger.info(
        f"Logging configured for {settings.environment} environment "
        f"with level {settings.log_level.upper()}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__ in modules)
    
    Returns:
        Configured logger instance
    
    Example:
        logger = get_logger(__name__)
        logger.info("Processing request")
    """
    return logging.getLogger(name)


__all__ = [
    'get_log_config',
    'setup_logging',
    'get_logger'
]
