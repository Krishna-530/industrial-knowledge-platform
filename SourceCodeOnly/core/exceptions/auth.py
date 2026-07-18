from typing import Any, Dict, Optional
from core.exceptions.base import AppException

class UnauthorizedError(AppException):
    def __init__(self, message: str = "Not authenticated", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=401, message=message, details=details)

class ForbiddenError(AppException):
    def __init__(self, message: str = "Operation not permitted", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=403, message=message, details=details)
