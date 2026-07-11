from typing import List
from app.retrieval.interfaces import AbstractRetrievalStrategy
from app.search.schemas import SearchQuery
from app.retrieval.schemas import SearchHit
from app.search.search_service import SearchService

class KeywordRetrievalStrategy(AbstractRetrievalStrategy):
    """
    Delegates to the existing SearchService (Postgres FTS) to get keyword hits.
    """
    def __init__(self, search_service: SearchService):
        self.search_service = search_service

    async def fetch_hits(self, query: SearchQuery) -> tuple[List[SearchHit], int, bool]:
        search_result_page = await self.search_service.search(query)
        
        hits = []
        for item in search_result_page.items:
            # Map from SearchResult to internal SearchHit
            hits.append(SearchHit(
                document_id=item.document_id,
                version_id=item.document_version_id,
                score=item.score,
                highlight=item.highlight or "",
                language=item.language
            ))
            
        return hits, search_result_page.total_count, search_result_page.has_more
