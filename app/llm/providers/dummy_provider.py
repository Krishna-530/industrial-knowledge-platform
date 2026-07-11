from typing import AsyncGenerator, Any
from app.llm.interfaces.provider import AbstractLLMProvider
from app.llm.models.context import ExecutionContext, ExecutionState
from app.llm.models.request import LLMRequest
from app.llm.providers.adapters.dummy_adapter import DummyAdapter

class DummyProvider(AbstractLLMProvider):
    def __init__(self):
        self.adapter = DummyAdapter()
        
    @property
    def provider_name(self) -> str:
        return "dummy_provider"

    async def initialize(self) -> None:
        pass
    
    async def shutdown(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True

    async def generate(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest) -> Any:
        mapped_req = self.adapter.map_request(request)
        return await self.adapter.invoke_sdk(mapped_req)

    async def stream(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest) -> AsyncGenerator[Any, None]:
        mapped_req = self.adapter.map_request(request)
        async for chunk in self.adapter.invoke_stream(mapped_req):
            yield chunk
