from core.settings import Settings
from app.services.embedding.base import AbstractEmbeddingProvider
from app.services.embedding.openai_provider import OpenAIEmbeddingProvider

class ProviderFactory:
    @staticmethod
    def get_provider(settings: Settings) -> AbstractEmbeddingProvider:
        # Currently only supports openai, can be expanded to check settings.llm_provider
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model if hasattr(settings, 'openai_model') else "text-embedding-3-small",
            timeout=settings.embedding_timeout_seconds,
            retry_limit=settings.embedding_retry_limit
        )
