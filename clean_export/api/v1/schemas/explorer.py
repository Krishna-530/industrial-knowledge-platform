from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID

class ExplorerChunkResponse(BaseModel):
    id: UUID
    index: int
    text: str
    token_count: Optional[int] = None
    embedding_status: str

class ExplorerEntityResponse(BaseModel):
    id: str
    name: str
    category: str
    confidence: float

class ExplorerRelationshipResponse(BaseModel):
    id: str
    subject_id: str
    subject_name: str
    predicate: str
    object_id: str
    object_name: str
    quality_score: float
    status: str

class DocumentExplorerResponse(BaseModel):
    document_id: UUID
    chunks: List[ExplorerChunkResponse]
    entities: List[ExplorerEntityResponse]
    relationships: List[ExplorerRelationshipResponse]
