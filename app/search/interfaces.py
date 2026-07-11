from typing import Protocol
from uuid import UUID
from app.search.schemas import SearchQuery, SearchResultPage

class AbstractSearchProvider(Protocol):
    async def index_document(self, document_version_id: UUID, content: str, language: str, metadata: dict) -> None:
        """Inserts or updates a new document into the search index."""
        ...
        
    async def update_document(self, document_version_id: UUID, content: str, language: str, metadata: dict) -> None:
        """Updates an existing document in the search index."""
        ...
        
    async def delete_document(self, document_version_id: UUID) -> None:
        """Removes a document from the search index."""
        ...
        
    async def clear_previous_versions(self, document_id: UUID, exclude_version_id: UUID) -> None:
        """Clears search vectors for all older versions of a document."""
        ...
        
    async def rebuild_index(self, batch_size: int = 100) -> None:
        """Rebuilds the entire search index from source truth."""
        ...
        
    async def search(self, query: SearchQuery) -> SearchResultPage:
        """Executes a search query and returns normalized results (including highlights)."""
        ...
        
    async def health_check(self) -> bool:
        """Verifies connection and health of the search backend."""
        ...
