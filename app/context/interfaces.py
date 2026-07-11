from abc import ABC, abstractmethod
from typing import List
from app.context.schemas import ContextChunk, FormattedContext

class AbstractTokenCounter(ABC):
    """
    Generic abstraction for context sizing, regardless of the underlying tokenizer.
    """
    @abstractmethod
    def count(self, text: str) -> int:
        pass

class AbstractContextFormatter(ABC):
    """
    Formats the finalized chunks into a specific string structure (XML, Markdown).
    Must not contain truncation logic.
    """
    @abstractmethod
    def format_chunks(self, chunks: List[ContextChunk]) -> FormattedContext:
        pass

class AbstractPackingStrategy(ABC):
    """
    Defines the strategy for packing chunks into a given token budget.
    (e.g., GreedyPacking, SemanticClustering).
    """
    @abstractmethod
    def pack(self, chunks: List[ContextChunk], max_tokens: int, counter: AbstractTokenCounter) -> tuple[List[ContextChunk], int]:
        """
        Returns a tuple of (packed_chunks, total_estimated_tokens)
        """
        pass
