from abc import ABC, abstractmethod
from typing import AsyncGenerator
from app.llm.models.context import ExecutionContext, ExecutionState
from app.llm.models.request import LLMRequest

class AbstractLLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def initialize(self) -> None:
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass

    @abstractmethod
    async def generate(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest) -> any:
        # returns RawProviderResponse
        pass

    @abstractmethod
    async def stream(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest) -> AsyncGenerator[any, None]:
        # yields RawStreamChunk
        pass
