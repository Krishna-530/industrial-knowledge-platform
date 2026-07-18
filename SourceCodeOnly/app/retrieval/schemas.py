from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.search.schemas import SearchQuery

class SearchHit(BaseModel):
    """Internal DTO representing a raw hit from the search provider."""
    document_id: UUID
    version_id: UUID
    score: float
    highlight: str
    language: str

class RetrievalRequest(BaseModel):
    """Request DTO for retrieving knowledge."""
    search_query: SearchQuery
    latest_only: bool = True
    include_metadata: bool = True
    include_content: bool = True
    max_documents: Optional[int] = Field(None, description="Max documents to return (for future context window limits)")
    max_content_length: Optional[int] = Field(None, description="Max content length per document (future use)")
    requesting_user_id: UUID

class KnowledgeDocument(BaseModel):
    """The canonical assembled truth object returned by Retrieval."""
    document_id: UUID
    version_id: UUID
    title: str
    metadata: Dict[str, Any]
    highlight: str
    full_content: Optional[str]
    score: float
    language: str
    
    # Provenance fields
    version_number: int
    indexed_at: Optional[datetime]
    retrieved_at: datetime
    source_uri: Optional[str]
    provider_name: str

class RetrievalResult(BaseModel):
    """The final result payload for a retrieval request."""
    items: List[KnowledgeDocument]
    total_count: int
    has_more: bool

class RetrievalTelemetry(BaseModel):
    """Telemetry data output by the Retrieval Service."""
    retrieval_started: datetime
    retrieval_completed: datetime
    retrieval_duration_ms: float
    hydration_duration_ms: float
    documents_found: int
    documents_returned: int
    permission_filtered: int
    retrieval_strategy: str
