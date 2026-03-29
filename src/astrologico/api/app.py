"""
FastAPI application factory and configuration.

Creates and configures the main API application with CORS, middleware, and routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.astrologico.api.settings import settings
from src.astrologico.api.routes import chart, planets, aspects, moon, ask, status


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(status.router)
    app.include_router(chart.router)
    app.include_router(planets.router)
    app.include_router(aspects.router)
    app.include_router(moon.router)
    app.include_router(ask.router)
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level=settings.log_level
    )
