import pybreaker
import logging
from typing import List, Type, TypeVar, Any, Dict
from pydantic import BaseModel
from app.extraction.providers.base import AbstractExtractionProvider

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class ProviderRouter:
    """
    Routes extraction requests to the primary provider, and gracefully fails over 
    to secondary providers using exponential circuit breakers.
    """
    def __init__(self, providers: List[AbstractExtractionProvider]):
        if not providers:
            raise ValueError("At least one provider must be configured.")
        self.providers = providers
        # Open circuit after 5 consecutive failures, try to close after 60 seconds
        self.breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

    async def route_extraction(
        self,
        text: str,
        response_model: Type[T],
        system_prompt: str
    ) -> tuple[T, Dict[str, Any]]:
        
        last_exception = None
        for provider in self.providers:
            try:
                # We wrap the provider call in the circuit breaker
                return await self._execute_with_breaker(provider, text, response_model, system_prompt)
            except pybreaker.CircuitBreakerError as e:
                logger.warning(f"Circuit breaker open for provider {provider.provider_name}. Trying next.")
                last_exception = e
            except Exception as e:
                # If it's a rate limit (429) or 500 error, log and failover
                logger.error(f"Provider {provider.provider_name} failed: {e}. Failing over.")
                last_exception = e
                
        # If all providers fail or break, raise the last exception back to the boundary
        raise RuntimeError(f"All extraction providers failed. Last error: {last_exception}") from last_exception

    async def _execute_with_breaker(self, provider: AbstractExtractionProvider, text: str, response_model: Type[T], system_prompt: str):
        @self.breaker
        async def call_provider():
            return await provider.extract(text, response_model, system_prompt)
        return await call_provider()
