from core.exceptions.base import (
    AppException,
    ValidationException,
    NotFoundError,
    InternalServerError,
    ConfigurationError
)
from core.exceptions.auth import UnauthorizedError, ForbiddenError
from core.exceptions.document import (
    EntityNotFoundError,
    DuplicateEntityError,
    DocumentContentException,
    DocumentContentPersistenceException
)
from core.exceptions.processing import (
    ProcessingFailedException,
    ProcessingValidationException,
    UnsupportedFormatError
)
from core.exceptions.storage import StorageException
from core.exceptions.workflow import WorkflowException, EventDispatchException

__all__ = [
    "AppException",
    "ValidationException",
    "NotFoundError",
    "InternalServerError",
    "ConfigurationError",
    "UnauthorizedError",
    "ForbiddenError",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "DocumentContentException",
    "DocumentContentPersistenceException",
    "ProcessingFailedException",
    "ProcessingValidationException",
    "UnsupportedFormatError",
    "StorageException",
    "WorkflowException",
    "EventDispatchException",
]
