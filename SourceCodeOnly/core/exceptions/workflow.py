from typing import Any, Dict, Optional
from core.exceptions.base import AppException

class WorkflowException(AppException):
    def __init__(self, message: str = "Workflow error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, message=message, details=details)

class EventDispatchException(AppException):
    def __init__(self, message: str = "Event dispatch error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, message=message, details=details)
