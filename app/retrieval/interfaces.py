from typing import List
from abc import ABC, abstractmethod

from app.search.schemas import SearchQuery
from app.retrieval.schemas import SearchHit

class AbstractRetrievalStrategy(ABC):
    """
    Interface for fetching SearchHit objects from a backend.
    """
    @abstractmethod
    async def fetch_hits(self, query: SearchQuery) -> tuple[List[SearchHit], int, bool]:
        """
        Returns (hits, total_count, has_more)
        """
        pass

class AbstractRanker(ABC):
    """
    Interface for merging and ranking hits from multiple strategies.
    """
    @abstractmethod
    def rank(self, hit_lists: List[List[SearchHit]], query: SearchQuery) -> List[SearchHit]:
        pass
