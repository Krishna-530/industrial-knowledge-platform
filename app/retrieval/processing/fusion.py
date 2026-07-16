from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ResultFusionEngine:
    """
    Normalizes and fuses results from diverse retrieval strategies (Graph, Semantic, Keyword).
    Provides a unified ranking layer before budgeting.
    """
    
    @staticmethod
    def fuse(graph_results: List[Dict[str, Any]], semantic_results: List[Dict[str, Any]], keyword_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        fused = []
        
        # 1. Normalize graph scores (0.0 to 1.0 based on quality_score)
        for g in graph_results:
            fused.append({
                "type": "GRAPH",
                "content": g,
                "normalized_score": g.get("quality_score", 0.5) * 1.2 # Graph answers are often highly precise, slight boost
            })
            
        # 2. Normalize semantic scores (assume cosine distance/similarity)
        for s in semantic_results:
            fused.append({
                "type": "SEMANTIC",
                "content": s,
                "normalized_score": s.get("score", 0.5) * 0.9
            })
            
        # 3. Normalize keyword scores (TF-IDF / BM25)
        # Assuming BM25 scores can exceed 1.0, we normalize or cap them.
        for k in keyword_results:
            fused.append({
                "type": "KEYWORD",
                "content": k,
                "normalized_score": min(k.get("score", 1.0) / 10.0, 0.8) # Arbitrary normalization stub
            })
            
        # 4. Global Ranking
        fused.sort(key=lambda x: x["normalized_score"], reverse=True)
        
        logger.info(f"Fusion Engine unified {len(fused)} total retrieval items.")
        return fused
