from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GraphContextBudgetService:
    """
    Sub-allocator. Ensures the Graph slice doesn't exceed its portion of the prompt budget.
    """
    def __init__(self):
        # We assume 4 characters per token as a rough heuristic for speed.
        self.CHARS_PER_TOKEN = 4

    def trim_to_budget(self, edges: List[Dict[str, Any]], max_tokens: int) -> List[Dict[str, Any]]:
        max_chars = max_tokens * self.CHARS_PER_TOKEN
        
        current_chars = 0
        budgeted_edges = []
        
        for edge in edges:
            # Estimate string size of the edge representation
            edge_chars = len(str(edge))
            
            if current_chars + edge_chars > max_chars:
                logger.debug(f"Graph budget exhausted. Dropping {len(edges) - len(budgeted_edges)} edges.")
                break
                
            current_chars += edge_chars
            budgeted_edges.append(edge)
            
        return budgeted_edges
