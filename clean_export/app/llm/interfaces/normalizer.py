from abc import ABC, abstractmethod
from typing import Any
from app.llm.models.response import ExecutionResult, StreamChunk

class AbstractResponseNormalizer(ABC):
    @abstractmethod
    def normalize(self, raw_response: Any) -> ExecutionResult:
        pass

class AbstractStreamNormalizer(ABC):
    @abstractmethod
    def normalize_chunk(self, raw_chunk: Any) -> StreamChunk:
        pass
