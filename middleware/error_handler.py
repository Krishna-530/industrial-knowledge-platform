import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from core.exceptions import AppException

logger = logging.getLogger(__name__)

def setup_exception_handlers(app) -> None:
    """Register global exception handlers for the application."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        request_id = getattr(request.state, "request_id", None)
        logger.error(
            f"Application exception: {exc.message}",
            extra={"request_id": request_id, "details": exc.details, "status_code": exc.status_code}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", None)
        logger.warning(
            f"Validation error",
            extra={"request_id": request_id, "errors": exc.errors()}
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "Validation Error",
                "details": exc.errors(),
                "request_id": request_id
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        logger.exception(
            f"Unhandled exception: {str(exc)}",
            extra={"request_id": request_id}
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal Server Error",
                "request_id": request_id
            },
        )
