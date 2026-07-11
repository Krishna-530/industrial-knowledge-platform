from typing import List, Tuple
from app.context.interfaces import AbstractPackingStrategy, AbstractTokenCounter
from app.context.schemas import ContextChunk

class GreedyPackingStrategy(AbstractPackingStrategy):
    """
    Packs chunks until the max token budget is reached.
    Truncation is currently at the chunk boundary (drops the whole chunk if it exceeds).
    """
    def pack(self, chunks: List[ContextChunk], max_tokens: int, counter: AbstractTokenCounter) -> Tuple[List[ContextChunk], int]:
        packed = []
        current_tokens = 0
        
        for chunk in chunks:
            estimate = counter.count(chunk.content)
            chunk.token_estimate = estimate
            
            if current_tokens + estimate <= max_tokens:
                packed.append(chunk)
                current_tokens += estimate
            else:
                # We reached the budget
                break
                
        return packed, current_tokens
