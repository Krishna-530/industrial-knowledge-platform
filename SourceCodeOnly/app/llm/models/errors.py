class ProviderError(Exception):
    """Base exception for all normalized provider errors."""

class ProviderUnavailable(ProviderError):
    """Provider endpoint is unreachable or down."""

class InvalidRequest(ProviderError):
    """Provider rejected the request as invalid (e.g., bad format)."""

class RateLimited(ProviderError):
    """Provider rate limit exceeded (429)."""

class AuthenticationFailed(ProviderError):
    """Provider rejected authentication credentials."""

class TimeoutError(ProviderError):
    """Request exceeded provider timeout."""

class ContentFiltered(ProviderError):
    """Provider refused to fulfill request due to content safety policy."""

class ContextTooLarge(ProviderError):
    """Prompt payload exceeded model context window size."""
