from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EvidenceDeduplicationService:
    """
    Prevents the LLM prompt from being flooded with redundant chunk texts.
    If Node A -> Node B and Node B -> Node C both rely on Chunk 17, 
    we only want Chunk 17 appearing once in the overall context payload.
    """
    
    @staticmethod
    def deduplicate(edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_chunks = set()
        deduplicated = []
        
        for edge in edges:
            chunk_id = edge.get("chunk_id")
            if chunk_id:
                if chunk_id in seen_chunks:
                    # We can retain the structural edge but strip the heavy text payload
                    # to save context budget.
                    edge["supporting_text"] = "[See above chunk]"
                else:
                    seen_chunks.add(chunk_id)
            deduplicated.append(edge)
            
        return deduplicated
