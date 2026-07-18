from typing import List
from app.context.schemas import ContextChunk

class ChunkSelector:
    """
    Selects relevant chunks based on criteria or dynamic filtering.
    For Phase 6.2, it is a pass-through, but establishes the boundary 
    where irrelevant extracted chunks can be dropped before compression.
    """
    def select(self, chunks: List[ContextChunk]) -> List[ContextChunk]:
        return chunks
