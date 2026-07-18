from typing import Any, AsyncGenerator
import asyncio
from app.llm.interfaces.adapter import AbstractSDKAdapter
from app.llm.models.request import LLMRequest
from app.llm.models.errors import ProviderError

class DummyAdapter(AbstractSDKAdapter):
    def map_request(self, request: LLMRequest) -> Any:
        # Dummy mapping just passes the payload through as a dict
        return request.model_dump()
        
    async def invoke_sdk(self, mapped_payload: Any) -> Any:
        # Dummy implementation returning a raw dict
        return {
            "id": "dummy-123",
            "content": "This is a dummy response.",
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "finish_reason": "stop"
        }
        
    async def invoke_stream(self, mapped_payload: Any) -> AsyncGenerator[Any, None]:
        chunks = [
            {"id": "dummy-123", "delta": "This "},
            {"id": "dummy-123", "delta": "is a "},
            {"id": "dummy-123", "delta": "dummy stream.", "finish_reason": "stop"}
        ]
        for chunk in chunks:
            yield chunk
            await asyncio.sleep(0.01)
            
    def translate_error(self, error: Exception) -> ProviderError:
        return ProviderError(str(error))
