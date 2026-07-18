from typing import Any, Dict, Optional
from core.exceptions.base import AppException, NotFoundError

class EntityNotFoundError(NotFoundError):
    def __init__(self, message: str = "Entity not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, details=details)

class DuplicateEntityError(AppException):
    def __init__(self, message: str = "Entity already exists", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=409, message=message, details=details)

class DocumentContentException(AppException):
    def __init__(self, message: str = "Document content error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=400, message=message, details=details)

class DocumentContentPersistenceException(AppException):
    def __init__(self, message: str = "Document content persistence error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, message=message, details=details)
