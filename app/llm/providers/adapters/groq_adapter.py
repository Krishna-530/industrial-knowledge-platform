from typing import Any, AsyncGenerator, Dict, List
import groq
from app.llm.interfaces.adapter import AbstractSDKAdapter
from app.llm.models.request import LLMRequest
from app.llm.models.errors import (
    ProviderError,
    RateLimited,
    TimeoutError,
    AuthenticationFailed,
    InvalidRequest,
    ProviderUnavailable
)

class GroqAdapter(AbstractSDKAdapter):
    def map_request(self, request: LLMRequest) -> Dict[str, Any]:
        """
        Maps the domain LLMRequest to Groq's ChatCompletion kwargs.
        """
        kwargs = {
            "model": request.payload.model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in request.payload.messages
            ],
            "temperature": request.config.temperature,
            "top_p": request.config.top_p,
        }
        
        if request.config.max_tokens:
            kwargs["max_tokens"] = request.config.max_tokens
            
        if request.config.stop_sequences:
            kwargs["stop"] = request.config.stop_sequences
            
        if request.config.response_format:
            kwargs["response_format"] = {"type": request.config.response_format}
            
        return kwargs

    async def invoke_sdk(self, mapped_payload: Any) -> Any:
        # Not used here as GroqProvider directly invokes the SDK. 
        # But required by interface if we used a pure abstraction.
        raise NotImplementedError("Use GroqProvider directly")

    async def invoke_stream(self, mapped_payload: Any) -> AsyncGenerator[Any, None]:
        raise NotImplementedError("Use GroqProvider directly")

    def translate_error(self, error: Exception) -> ProviderError:
        """
        Translates groq.APIError to ProviderError domain exceptions.
        """
        if isinstance(error, groq.RateLimitError):
            # Try to extract retry-after header if possible
            retry_after = error.response.headers.get('retry-after') if error.response else None
            # Store in exception args for the caller to parse
            return RateLimited(str(error), retry_after)
            
        if isinstance(error, groq.AuthenticationError):
            return AuthenticationFailed(str(error))
            
        if isinstance(error, groq.BadRequestError):
            return InvalidRequest(str(error))
            
        if isinstance(error, groq.APITimeoutError):
            return TimeoutError(str(error))
            
        if isinstance(error, (groq.APIConnectionError, groq.InternalServerError)):
            return ProviderUnavailable(str(error))
            
        # Fallback for other Groq errors or arbitrary exceptions
        return ProviderError(str(error))
