import logging
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from app.services.embedding.base import AbstractEmbeddingProvider, ProviderCapabilities
import openai
from openai import AsyncOpenAI
import time

logger = logging.getLogger(__name__)

class OpenAIEmbeddingProvider(AbstractEmbeddingProvider):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", timeout: int = 60, retry_limit: int = 5):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.retry_limit = retry_limit
        
        # Initialize client here. Will fail gracefully if api_key is None during health_check
        self.client = AsyncOpenAI(api_key=api_key or "invalid", timeout=timeout)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_batching=True,
            supports_usage_metrics=True,
            supports_async=True,
            supports_dimension_reporting=True,
            max_batch_size=2048, # OpenAI soft limit per request
            max_tokens=8192      # context limit
        )

    async def health_check(self) -> bool:
        if self.api_key is None or self.api_key == "invalid":
            logger.error({"event": "ProviderHealthCheckFailed", "reason": "Missing API Key"})
            return False
            
        try:
            # simple single token embedding to verify key and model
            await self.client.embeddings.create(input=["hello"], model=self.model)
            return True
        except openai.AuthenticationError:
            logger.error({"event": "ProviderHealthCheckFailed", "reason": "AuthenticationError"})
            return False
        except Exception as e:
            logger.error({"event": "ProviderHealthCheckFailed", "error": str(e)})
            return False

    # Retry on RateLimits and Server errors, but fast-fail on Auth/BadRequests
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError)),
        wait=wait_exponential_jitter(initial=1, max=60),
        stop=stop_after_attempt(5),
        reraise=True
    )
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        start_time = time.perf_counter()
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            
            processing_ms = int((time.perf_counter() - start_time) * 1000)
            token_usage = response.usage.total_tokens
            
            # OpenAI specific cost estimation: ~$0.02 / 1M tokens for 3-small
            cost_per_token = 0.02 / 1_000_000
            estimated_cost = token_usage * cost_per_token
            
            # Emit strict payload
            logger.info({
                "event": "ProviderBatchCompleted",
                "provider": "openai",
                "model": self.model,
                "batch_size": len(texts),
                "token_usage": token_usage,
                "processing_ms": processing_ms,
                "estimated_cost": f"{estimated_cost:.6f}"
            })
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            logger.error({
                "event": "ProviderBatchFailed",
                "provider": "openai",
                "model": self.model,
                "error": str(e)
            })
            raise
