"""
Error handling middleware for Astrologico API.

Provides comprehensive exception handling, error transformation to HTTP responses,
structured error logging, and client-friendly error messages.
"""

import logging
import traceback
from typing import Callable, Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from astrologico.api.settings import settings

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standard error response format."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 500,
        details: Optional[dict] = None,
        request_id: Optional[str] = None
    ):
        """
        Create an error response.
        
        Args:
            error_code: Machine-readable error code (e.g., "INVALID_COORDINATES")
            message: Human-readable error message
            status_code: HTTP status code
            details: Optional additional error details
            request_id: Optional request correlation ID
        """
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.request_id = request_id
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        response = {
            "error": {
                "code": self.error_code,
                "message": self.message
            }
        }
        
        if self.details:
            response["error"]["details"] = self.details
        
        if self.request_id:
            response["request_id"] = self.request_id
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive error handling.
    
    Features:
    - Catches all unhandled exceptions
    - Transforms exceptions to HTTP responses
    - Logs errors with full context
    - Returns consistent error format
    - Hides sensitive details in production
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and handle any exceptions.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
        
        Returns:
            HTTP response (error or normal)
        """
        try:
            response = await call_next(request)
            return response
        
        except Exception as exc:
            # Get request ID if available
            request_id = request.scope.get("request_id")
            
            # Log the error with full traceback
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query_string": request.url.query,
                },
                exc_info=True
            )
            
            # Create error response
            error_response = self._get_error_response(exc, request_id)
            
            return JSONResponse(
                status_code=error_response.status_code,
                content=error_response.to_dict()
            )
    
    def _get_error_response(
        self,
        exc: Exception,
        request_id: Optional[str] = None
    ) -> ErrorResponse:
        """
        Transform exception to ErrorResponse.
        
        Args:
            exc: The exception that occurred
            request_id: Request correlation ID
        
        Returns:
            ErrorResponse object
        """
        # Map exception types to error codes and messages
        exception_mapping = {
            ValueError: ("INVALID_VALUE", 400, "Invalid input value"),
            KeyError: ("NOT_FOUND", 404, "Resource not found"),
            TypeError: ("TYPE_ERROR", 400, "Invalid request type"),
            FileNotFoundError: ("RESOURCE_NOT_FOUND", 404, "Resource not found"),
        }
        
        # Check if exception type has a mapping
        for exc_type, (error_code, status_code, message) in exception_mapping.items():
            if isinstance(exc, exc_type):
                details = None
                if settings.is_development():
                    details = {"exception_type": exc_type.__name__, "details": str(exc)}
                
                return ErrorResponse(
                    error_code=error_code,
                    message=message or str(exc),
                    status_code=status_code,
                    details=details,
                    request_id=request_id
                )
        
        # Default to generic server error
        details = None
        if settings.is_development():
            details = {
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc()
            }
        
        return ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred" if settings.is_production() else str(exc),
            status_code=500,
            details=details,
            request_id=request_id
        )


class HTTPExceptionHandler:
    """
    Handler for FastAPI HTTPException instances.
    
    Provides consistent error response format for HTTP exceptions.
    """
    
    @staticmethod
    def to_error_response(
        exc,  # HTTPException
        request_id: Optional[str] = None
    ) -> ErrorResponse:
        """
        Convert HTTPException to ErrorResponse.
        
        Args:
            exc: HTTPException instance
            request_id: Request correlation ID
        
        Returns:
            ErrorResponse object
        """
        # Extract error code from detail if present
        detail = exc.detail
        error_code = "HTTP_ERROR"
        message = str(detail)
        
        # Try to extract error code from detail message
        if isinstance(detail, str) and ":" in detail:
            parts = detail.split(":", 1)
            error_code = parts[0].upper().strip()
            message = parts[1].strip()
        
        return ErrorResponse(
            error_code=error_code,
            message=message,
            status_code=exc.status_code,
            request_id=request_id
        )


__all__ = [
    'ErrorResponse',
    'ErrorHandlingMiddleware',
    'HTTPExceptionHandler'
]
