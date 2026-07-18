import abc
from dataclasses import dataclass
from typing import List

@dataclass
class ProviderCapabilities:
    supports_batching: bool
    supports_usage_metrics: bool
    supports_async: bool
    supports_dimension_reporting: bool
    max_batch_size: int
    max_tokens: int

class AbstractEmbeddingProvider(abc.ABC):
    """
    Abstract interface for all embedding providers.
    """
    
    @abc.abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        pass

    @abc.abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Takes a batch of texts and returns a list of embeddings.
        Should natively emit provider-specific telemetry and handle HTTP layer retries.
        """
        pass

    @abc.abstractmethod
    async def health_check(self) -> bool:
        """
        Verifies API key validity, network reachability, and model existence.
        """
        pass
