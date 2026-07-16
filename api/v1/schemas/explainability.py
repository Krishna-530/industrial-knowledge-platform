from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

class CitationChunk(BaseModel):
    chunk_id: str
    document_id: str
    text_snippet: str
    score: float

class ProvenanceTrace(BaseModel):
    id: str = Field(..., description="Unique provenance ID")
    relationship_id: str = Field(..., description="The ID of the graph edge")
    confidence_score: float = Field(..., description="Provider extraction confidence")
    supporting_chunks: List[CitationChunk] = Field(default_factory=list)

class EvidenceResponse(BaseModel):
    traces: List[ProvenanceTrace]
    
class StreamingMessage(BaseModel):
    event: str
    data: Dict[str, Any]
