from typing import List, Dict, Any
from app.retrieval.planners.dto import RankingProfileType
from app.retrieval.policy_engine import RetrievalPolicy

class GraphRankingService:
    """
    Ranks the raw edges returned by the Traversal Engine before LLM formatting.
    """
    def __init__(self, policy: RetrievalPolicy):
        self.policy = policy

    def rank(self, edges: List[Dict[str, Any]], profile: RankingProfileType) -> List[Dict[str, Any]]:
        # This sorts the edge DTOs based on profile rules.
        # Example: TroubleShooting heavily weighs quality_score.
        
        def _score(edge: Dict[str, Any]) -> float:
            base_score = edge.get("quality_score", 0.0)
            if profile == RankingProfileType.TROUBLESHOOTING:
                # Boost certain predicates
                if edge.get("predicate") in ["CAUSES", "FAILS_BEFORE"]:
                    return base_score * 1.5
            return base_score
            
        ranked = sorted(edges, key=_score, reverse=True)
        return ranked[:self.policy.ranking_limit]
