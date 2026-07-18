from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator
from app.llm.models.request import LLMRequest
from app.llm.models.errors import ProviderError

class AbstractSDKAdapter(ABC):
    @abstractmethod
    def map_request(self, request: LLMRequest) -> Any:
        pass
    
    @abstractmethod
    async def invoke_sdk(self, mapped_payload: Any) -> Any:
        # returns RawProviderResponse
        pass
    
    @abstractmethod
    async def invoke_stream(self, mapped_payload: Any) -> AsyncGenerator[Any, None]:
        # yields RawStreamChunk
        pass
    
    @abstractmethod
    def translate_error(self, error: Exception) -> ProviderError:
        pass
