import logging
from app.search.interfaces import AbstractSearchProvider
from app.search.schemas import SearchQuery, SearchResultPage

logger = logging.getLogger(__name__)

class SearchService:
    """
    Orchestrates search queries against the underlying search provider.
    Strictly read-only operations.
    """
    def __init__(self, provider: AbstractSearchProvider):
        self.provider = provider

    async def search(self, query: SearchQuery) -> SearchResultPage:
        # Validate or sanitize query here if needed
        logger.info({"event": "search_requested", "query_text": query.query_text, "language": query.language})
        return await self.provider.search(query)
        
    async def health_check(self) -> bool:
        return await self.provider.health_check()
