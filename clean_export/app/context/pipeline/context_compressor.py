from typing import List, Tuple
from app.context.schemas import ContextChunk

class ContextCompressor:
    """
    Identifies and removes duplicate or highly overlapping chunks.
    """
    def compress(self, chunks: List[ContextChunk]) -> Tuple[List[ContextChunk], int]:
        """
        Returns (compressed_chunks, duplicates_dropped_count)
        """
        unique_contents = set()
        compressed = []
        dropped = 0
        
        for chunk in chunks:
            if chunk.content not in unique_contents:
                unique_contents.add(chunk.content)
                compressed.append(chunk)
            else:
                dropped += 1
                
        return compressed, dropped
