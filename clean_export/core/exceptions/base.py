from typing import Any, Dict, Optional

class AppException(Exception):
    """Base exception for application errors."""
    def __init__(
        self,
        status_code: int = 500,
        message: str = "Internal Server Error",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ValidationException(AppException):
    def __init__(self, message: str = "Validation Error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=422, message=message, details=details)

class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=404, message=message, details=details)

class InternalServerError(AppException):
    def __init__(self, message: str = "Internal Server Error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, message=message, details=details)

class ConfigurationError(AppException):
    def __init__(self, message: str = "Configuration Error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, message=message, details=details)
