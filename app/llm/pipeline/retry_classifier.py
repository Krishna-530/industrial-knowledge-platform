from enum import Enum
from app.llm.models.errors import (
    ProviderError,
    RateLimited,
    TimeoutError,
    AuthenticationFailed,
    InvalidRequest,
    ContentFiltered,
    ContextTooLarge
)

class RetryAction(str, Enum):
    FATAL = "fatal"
    RETRYABLE = "retryable"

class RetryClassifier:
    def classify(self, error: Exception) -> RetryAction:
        if isinstance(error, (RateLimited, TimeoutError)):
            return RetryAction.RETRYABLE
        if isinstance(error, (AuthenticationFailed, InvalidRequest, ContentFiltered, ContextTooLarge)):
            return RetryAction.FATAL
        
        # Unmapped errors are considered fatal by default
        return RetryAction.FATAL
