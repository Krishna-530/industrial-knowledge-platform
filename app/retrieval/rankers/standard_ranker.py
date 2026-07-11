from typing import List
from app.retrieval.interfaces import AbstractRanker
from app.search.schemas import SearchQuery
from app.retrieval.schemas import SearchHit

class StandardRanker(AbstractRanker):
    """
    Pass-through ranker for when there is only one strategy, 
    or just sorts by score descending if multiple strategies are used.
    Future: Reciprocal Rank Fusion (RRF) for Hybrid search.
    """
    def rank(self, hit_lists: List[List[SearchHit]], query: SearchQuery) -> List[SearchHit]:
        if not hit_lists:
            return []
            
        if len(hit_lists) == 1:
            return hit_lists[0]
            
        # If multiple, flatten and sort by score (naive merge, replace with RRF later)
        all_hits = []
        for lst in hit_lists:
            all_hits.extend(lst)
            
        # De-duplicate by version_id, keeping highest score
        unique_hits = {}
        for hit in all_hits:
            if hit.version_id not in unique_hits or hit.score > unique_hits[hit.version_id].score:
                unique_hits[hit.version_id] = hit
                
        sorted_hits = sorted(unique_hits.values(), key=lambda h: h.score, reverse=True)
        return sorted_hits
