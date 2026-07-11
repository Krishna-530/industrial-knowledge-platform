from typing import Dict
from app.llm.interfaces.provider import AbstractLLMProvider

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, AbstractLLMProvider] = {}

    def register(self, provider: AbstractLLMProvider) -> None:
        self._providers[provider.provider_name] = provider

    def get_provider(self, name: str) -> AbstractLLMProvider:
        if name not in self._providers:
            raise ValueError(f"Provider {name} not found in registry")
        return self._providers[name]
