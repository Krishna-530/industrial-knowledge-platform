from typing import List
from app.context.schemas import ContextChunk, ContextOrderingStrategy

class ContextRanker:
    """
    Dedicated ranker for the Context domain.
    """
    def rank(self, chunks: List[ContextChunk], strategy: ContextOrderingStrategy) -> List[ContextChunk]:
        if strategy == ContextOrderingStrategy.CHRONOLOGICAL:
            # Placeholder for chronological sorting if dates were in ContextChunk
            pass
        elif strategy == ContextOrderingStrategy.RELEVANCE:
            chunks.sort(key=lambda c: c.rank_score, reverse=True)
            
        return chunks
