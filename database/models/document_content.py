import uuid
from datetime import datetime, timezone
from typing import Optional, Dict
from sqlalchemy import Integer, ForeignKey, DateTime, Text, Enum as SQLAlchemyEnum, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from database.models.base import Base
from core.enums.processing_status import ProcessingStatus

class DocumentContent(Base):
    __tablename__ = "document_contents"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("document_versions.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False
    )
    
    document_version: Mapped["DocumentVersion"] = relationship(
        "DocumentVersion",
        back_populates="content",
        lazy="selectin"
    )
    
    # Processing State
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SQLAlchemyEnum(ProcessingStatus, name="processingstatus_enum"), 
        nullable=False, 
        default=ProcessingStatus.PENDING
    )
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Extraction Results
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    character_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Metadata
    document_metadata: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    processing_metadata: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    
    # Audit
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Search & Indexing
    language: Mapped[str] = mapped_column(String, nullable=False, default="english")
    search_vector = mapped_column(TSVECTOR)
    
    __table_args__ = (
        Index('ix_document_contents_search_vector', 'search_vector', postgresql_using='gin'),
        {'extend_existing': True}
    )
