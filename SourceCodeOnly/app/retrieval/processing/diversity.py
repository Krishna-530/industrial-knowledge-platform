from typing import List, Dict, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ContextDiversityService:
    """
    Ensures that a single highly connected entity doesn't monopolize the result set.
    Caps edges per entity.
    """
    def __init__(self, max_edges_per_entity: int = 5):
        self.max_edges_per_entity = max_edges_per_entity

    def enforce_diversity(self, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        entity_counts = defaultdict(int)
        diverse_edges = []
        
        for edge in edges:
            sub = edge.get("subject_id")
            obj = edge.get("object_id")
            
            # If both ends are maxed out, skip
            if entity_counts[sub] >= self.max_edges_per_entity and entity_counts[obj] >= self.max_edges_per_entity:
                continue
                
            entity_counts[sub] += 1
            entity_counts[obj] += 1
            diverse_edges.append(edge)
            
        logger.debug(f"Diversity check: filtered {len(edges)} to {len(diverse_edges)} edges.")
        return diverse_edges
