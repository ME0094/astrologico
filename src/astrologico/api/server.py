"""
Astrologico API server entry point.

Provides CLI commands to start the Uvicorn ASGI server with proper configuration.
"""

import sys
import logging
from typing import Optional
import click
import uvicorn

from astrologico.api.settings import settings
from astrologico.api.logging_config import setup_logging

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--host",
    default=None,
    help="Server host (default: from ASTROLOGICO_API_HOST env var or 0.0.0.0)"
)
@click.option(
    "--port",
    type=int,
    default=None,
    help="Server port (default: from ASTROLOGICO_API_PORT env var or 8000)"
)
@click.option(
    "--workers",
    type=int,
    default=1,
    help="Number of worker processes (default: 1)"
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload on code changes (development only)"
)
@click.option(
    "--log-level",
    type=click.Choice(["critical", "error", "warning", "info", "debug"]),
    default=None,
    help="Logging level (default: from settings)"
)
def main(
    host: Optional[str],
    port: Optional[int],
    workers: int,
    reload: bool,
    log_level: Optional[str]
):
    """
    Start the Astrologico API server.
    
    Environment Variables:
    - ASTROLOGICO_ENV: Deployment environment (development, testing, production)
    - ASTROLOGICO_API_HOST: Server host to bind to
    - ASTROLOGICO_API_PORT: Server port
    - ASTROLOGICO_LOG_LEVEL: Logging level
    - OPENAI_API_KEY or ANTHROPIC_API_KEY: AI provider credentials
    """
    # Setup logging
    setup_logging()
    
    # Use provided values or fall back to settings
    server_host = host or settings.api_host
    server_port = port or settings.api_port
    server_log_level = log_level or settings.log_level.lower()
    
    # Validate production environment
    if settings.is_production():
        if server_host == "0.0.0.0":
            logger.warning(
                "SECURITY WARNING: Running production server on 0.0.0.0. "
                "This should only be done behind a reverse proxy (nginx, haproxy, etc.)."
            )
        
        if reload:
            logger.error("Auto-reload is not allowed in production!")
            sys.exit(1)
    
    # Create uvicorn config
    uv_config = uvicorn.Config(
        "astrologico.api.app:app",
        host=server_host,
        port=server_port,
        workers=workers,
        reload=reload and settings.is_development(),
        log_level=server_log_level,
        access_log=True,
        use_colors=True if server_log_level == "debug" else False,
    )
    
    # Create and run server
    server = uvicorn.Server(uv_config)
    
    logger.info(
        f"Starting Astrologico API server "
        f"({settings.environment.upper()} environment)"
    )
    logger.info(f"API Docs: http://{server_host}:{server_port}/docs")
    logger.info(f"API Redoc: http://{server_host}:{server_port}/redoc")
    
    # Run the server
    sys.exit(server.run())


if __name__ == "__main__":
    main()
