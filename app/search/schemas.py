from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

class SearchQuery(BaseModel):
    query_text: str
    language: str = "english"
    limit: int = 10
    offset: int = 0
    sort_order: str = "relevance"
    # Filters
    category_id: Optional[UUID] = None
    tags: Optional[List[UUID]] = None
    document_ids: Optional[List[UUID]] = None

class SearchResult(BaseModel):
    document_id: UUID
    document_version_id: UUID
    score: float
    highlight: str
    title: str
    category_id: UUID

class SearchResultPage(BaseModel):
    items: List[SearchResult]
    total_count: int
    has_more: bool
