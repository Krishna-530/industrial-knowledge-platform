import groq
import httpx
from app.llm.providers.adapters.groq_adapter import GroqAdapter
from app.llm.models.errors import RateLimited, AuthenticationFailed

def test_groq_adapter_error_mapping():
    adapter = GroqAdapter()
    
    # Test 429 RateLimit
    mock_response = httpx.Response(429, headers={"retry-after": "5"})
    err = groq.RateLimitError("Rate limit exceeded", response=mock_response, body=None)
    mapped = adapter.translate_error(err)
    
    assert isinstance(mapped, RateLimited)
    assert getattr(mapped, "retry_after", None) == "5"

    # Test 401 Auth
    mock_response = httpx.Response(401)
    err = groq.AuthenticationError("Invalid API Key", response=mock_response, body=None)
    mapped = adapter.translate_error(err)
    
    assert isinstance(mapped, AuthenticationFailed)
