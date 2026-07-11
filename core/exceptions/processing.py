from typing import Any, Dict, Optional
from core.exceptions.base import AppException

class ProcessingFailedException(AppException):
    def __init__(self, message: str = "Processing failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, message=message, details=details)

class ProcessingValidationException(AppException):
    def __init__(self, message: str = "Processing validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=400, message=message, details=details)
        
class UnsupportedFormatError(AppException):
    def __init__(self, message: str = "Unsupported format", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=415, message=message, details=details)
