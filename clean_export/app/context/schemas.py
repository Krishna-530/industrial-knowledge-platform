from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ContextFormat(str, Enum):
    XML = "xml"
    MARKDOWN = "markdown"

class ContextOrderingStrategy(str, Enum):
    RELEVANCE = "relevance"
    CHRONOLOGICAL = "chronological"

class ContextConfig(BaseModel):
    max_tokens: int
    max_documents: Optional[int] = None
    max_chunks: Optional[int] = None
    max_chunk_size: Optional[int] = None
    formatter: ContextFormat
    ordering_strategy: ContextOrderingStrategy = ContextOrderingStrategy.RELEVANCE
    compression_enabled: bool = True

class ContextChunk(BaseModel):
    chunk_id: UUID
    document_id: UUID
    version_id: UUID
    source_uri: Optional[str]
    page_number: Optional[int]
    section: Optional[str]
    content: str
    score: float
    token_estimate: int
    
    # Extended provenance
    chunk_index: int
    retrieval_strategy: str
    rank_score: float

class FormattedContext(BaseModel):
    formatted_string: str
    format_type: ContextFormat

class AssemblyReport(BaseModel):
    total_chunks_extracted: int
    chunks_omitted_duplicates: int
    chunks_omitted_budget: int
    final_chunk_count: int
    compression_ratio: float
    reasons: List[str]

class ContextPayload(BaseModel):
    context: FormattedContext
    estimated_tokens: int
    token_counter: str
    assembly_duration_ms: float
    generated_at: datetime
    report: AssemblyReport
    conversation_summary: Optional[str] = None
