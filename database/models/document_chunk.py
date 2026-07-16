import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from database.models.base import Base

class ChunkStatus(str, enum.Enum):
    PENDING = "PENDING"
    CHUNKED = "CHUNKED"
    EMBEDDING_PENDING = "EMBEDDING_PENDING"
    VECTOR_PENDING = "VECTOR_PENDING"
    FAILED = "FAILED"
    REEMBED_REQUIRED = "REEMBED_REQUIRED"
    RETRY_PENDING = "RETRY_PENDING"
    PROCESSING = "PROCESSING"

class FailureReason(str, enum.Enum):
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    INVALID_API_KEY = "INVALID_API_KEY"
    INVALID_MODEL = "INVALID_MODEL"
    NETWORK = "NETWORK"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    document_version_id = Column(UUID(as_uuid=True), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    
    token_count = Column(Integer, nullable=False)
    character_count = Column(Integer, nullable=False)
    
    source_page = Column(Integer, nullable=True)
    heading = Column(String(512), nullable=True)
    section_path = Column(String(1024), nullable=True)
    language = Column(String(10), nullable=True)
    checksum = Column(String(64), nullable=False, index=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    chunking_version = Column(String(32), default="v1", nullable=False)
    
    status = Column(Enum(ChunkStatus, name="chunkstatus"), default=ChunkStatus.PENDING, nullable=False)
    
    # Future Phase 13.3 Embedding Fields
    embedding_provider = Column(String(128), nullable=True)
    embedding_model = Column(String(128), nullable=True)
    embedding_dimension = Column(Integer, nullable=True)
    embedding_version = Column(String(64), nullable=True)
    embedded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Analytics & Telemetry Fields
    failure_reason = Column(Enum(FailureReason, name="failurereason"), nullable=True)
    processing_ms = Column(Integer, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    token_usage = Column(Integer, nullable=True)
    estimated_cost = Column(String(32), nullable=True) # Stored as string to prevent float precision loss, or Float
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", backref="chunks")
    document_version = relationship("DocumentVersion", backref="chunks")
