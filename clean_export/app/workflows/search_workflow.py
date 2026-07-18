import logging
from app.search.search_service import SearchService
from app.search.schemas import SearchQuery, SearchResultPage

logger = logging.getLogger(__name__)

class SearchWorkflow:
    """
    Orchestrates search requests from the API.
    """
    def __init__(self, search_service: SearchService):
        self.search_service = search_service

    async def execute_search(self, query: SearchQuery) -> SearchResultPage:
        # Here we could inject RBAC filters into the query to ensure the user 
        # only sees documents they are allowed to see.
        return await self.search_service.search(query)
