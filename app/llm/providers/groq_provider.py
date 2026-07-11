import time
from typing import AsyncGenerator, Any
from groq import AsyncGroq
from app.llm.interfaces.provider import AbstractLLMProvider
from app.llm.models.context import ExecutionContext, ExecutionState
from app.llm.models.request import LLMRequest
from app.llm.providers.adapters.groq_adapter import GroqAdapter
from app.llm.providers.groq_config import GroqConfig

class GroqProvider(AbstractLLMProvider):
    def __init__(self, config: GroqConfig):
        self.config = config
        self.client = None
        self.adapter = GroqAdapter()
        
        # Health check caching
        self._last_health_check = 0.0
        self._is_healthy = False
        self._health_ttl_seconds = 60.0

    @property
    def provider_name(self) -> str:
        return "groq"

    async def initialize(self) -> None:
        """
        Lifecycle startup: Validates config, creates client.
        """
        self.client = AsyncGroq(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.total_timeout,
            max_retries=0 # We handle retries at the pipeline stage
        )

    async def shutdown(self) -> None:
        """
        Lifecycle shutdown: Cleans up the HTTPX connection pool.
        """
        if self.client:
            await self.client.close()

    async def health_check(self) -> bool:
        """
        Concrete health check fetching the models list. Uses caching to prevent rate limits.
        """
        now = time.time()
        if now - self._last_health_check < self._health_ttl_seconds:
            return self._is_healthy

        if not self.client:
            return False

        try:
            # Lightweight call to verify connectivity and API key
            await self.client.models.list(timeout=2.0)
            self._is_healthy = True
        except Exception:
            self._is_healthy = False
            
        self._last_health_check = now
        return self._is_healthy

    async def generate(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest) -> Any:
        mapped_kwargs = self.adapter.map_request(request)
        try:
            return await self.client.chat.completions.create(**mapped_kwargs)
        except Exception as e:
            raise self.adapter.translate_error(e)

    async def stream(self, context: ExecutionContext, state: ExecutionState, request: LLMRequest) -> AsyncGenerator[Any, None]:
        mapped_kwargs = self.adapter.map_request(request)
        mapped_kwargs["stream"] = True
        
        try:
            stream = await self.client.chat.completions.create(**mapped_kwargs)
            async for chunk in stream:
                yield chunk
        except Exception as e:
            raise self.adapter.translate_error(e)
