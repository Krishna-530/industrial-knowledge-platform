from typing import List, Tuple
from app.context.interfaces import AbstractPackingStrategy, AbstractTokenCounter
from app.context.schemas import ContextChunk, ContextConfig

class ContextBudgeter:
    """
    Enforces the limits using ContextConfig and an AbstractPackingStrategy.
    """
    def __init__(self, packing_strategy: AbstractPackingStrategy, token_counter: AbstractTokenCounter):
        self.packing_strategy = packing_strategy
        self.token_counter = token_counter

    def enforce_budget(self, chunks: List[ContextChunk], config: ContextConfig) -> Tuple[List[ContextChunk], int, int]:
        """
        Returns (packed_chunks, estimated_tokens, chunks_omitted)
        """
        initial_count = len(chunks)
        
        # Apply chunk count limit if specified
        if config.max_chunks and len(chunks) > config.max_chunks:
            chunks = chunks[:config.max_chunks]
            
        packed_chunks, total_tokens = self.packing_strategy.pack(chunks, config.max_tokens, self.token_counter)
        
        omitted = initial_count - len(packed_chunks)
        return packed_chunks, total_tokens, omitted
