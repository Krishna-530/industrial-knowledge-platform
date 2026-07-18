from typing import Any, Dict, Optional
from core.exceptions.base import AppException

class StorageException(AppException):
    def __init__(self, message: str = "Storage error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, message=message, details=details)
