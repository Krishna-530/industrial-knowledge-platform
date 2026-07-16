from typing import Protocol, Type, TypeVar, Any, Dict, Optional
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class AbstractExtractionProvider(Protocol):
    @property
    def provider_name(self) -> str:
        ...

    @property
    def model_name(self) -> str:
        ...

    async def extract(
        self,
        text: str,
        response_model: Type[T],
        system_prompt: str,
        max_retries: int = 3
    ) -> tuple[T, Dict[str, Any]]:
        """
        Extracts structured data from text using LLM JSON schema support via Instructor.
        Returns the parsed Pydantic object and a metadata dictionary containing usage/telemetry.
        """
        ...
