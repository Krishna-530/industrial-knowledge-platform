class ProviderError(Exception):
    """Base exception for all normalized provider errors."""
    pass

class ProviderUnavailable(ProviderError):
    """Provider endpoint is unreachable or down."""
    pass

class InvalidRequest(ProviderError):
    """Provider rejected the request as invalid (e.g., bad format)."""
    pass

class RateLimited(ProviderError):
    """Provider rate limit exceeded (429)."""
    pass

class AuthenticationFailed(ProviderError):
    """Provider rejected authentication credentials."""
    pass

class TimeoutError(ProviderError):
    """Request exceeded provider timeout."""
    pass

class ContentFiltered(ProviderError):
    """Provider refused to fulfill request due to content safety policy."""
    pass

class ContextTooLarge(ProviderError):
    """Prompt payload exceeded model context window size."""
    pass
