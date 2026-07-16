from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel

class ExtractedFactResult(BaseModel):
    asset_id: str
    property: str
    value: str
    start_offset: int
    end_offset: int

class AbstractKnowledgeExtractor(ABC):
    @abstractmethod
    async def extract(self, current_chunk_text: str, current_chunk_id: str, previous_chunk_text: str = None) -> List[ExtractedFactResult]:
        """
        Extracts structured knowledge facts from the given chunk and optional context window.
        """
