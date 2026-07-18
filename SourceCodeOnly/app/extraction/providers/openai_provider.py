import time
from typing import Type, TypeVar, Any, Dict
from pydantic import BaseModel
import instructor
from openai import AsyncOpenAI
from app.extraction.providers.base import AbstractExtractionProvider
from core.settings import Settings

T = TypeVar('T', bound=BaseModel)

class OpenAIProvider(AbstractExtractionProvider):
    def __init__(self, settings: Settings):
        self.settings = settings
        # instructor patches the client to return Pydantic objects natively
        self.client = instructor.from_openai(AsyncOpenAI(api_key=settings.openai_api_key))
        # Note: We anchor to a specific model version to prevent model drift
        self._model = getattr(settings, "openai_extraction_model", "gpt-4o-2024-05-13")

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def extract(
        self,
        text: str,
        response_model: Type[T],
        system_prompt: str,
        max_retries: int = 3
    ) -> tuple[T, Dict[str, Any]]:
        start_time = time.time()
        
        response, completion = await self.client.chat.completions.create_with_completion(
            model=self._model,
            response_model=response_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"### CHUNK START ###\n{text}\n### CHUNK END ###"}
            ],
            max_retries=max_retries
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        usage = completion.usage
        
        metadata = {
            "provider": self.provider_name,
            "model": self.model_name,
            "latency_ms": latency_ms,
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        }
        
        return response, metadata
