import uuid
from typing import Optional, List
from uuid6 import uuid7
from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, Enum as SQLEnum, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.models.base import Base, TimestampMixin
import enum

class RelationshipStatus(str, enum.Enum):
    DISCOVERED = "DISCOVERED"
    PENDING_EVIDENCE = "PENDING_EVIDENCE"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"

class Relationship(TimestampMixin, Base):
    """
    Canonical Edge representation in the SQL Source of Truth.
    Uses UUIDv7 for time-ordered locality without breaking alias merges.
    """
    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint('subject_id', 'predicate', 'object_id', name='uix_relationship_triple'),
        {'extend_existing': True}
    )

    # UUIDv7 acts as a sequential primary key
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    predicate: Mapped[str] = mapped_column(String, nullable=False, index=True)
    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[RelationshipStatus] = mapped_column(SQLEnum(RelationshipStatus), nullable=False, default=RelationshipStatus.DISCOVERED, index=True)
    
    # Evidence back-population
    evidence: Mapped[List["RelationshipEvidence"]] = relationship("RelationshipEvidence", back_populates="relationship", cascade="all, delete-orphan")


class RelationshipEvidence(TimestampMixin, Base):
    """
    Corroborating proof for a Relationship's existence.
    """
    __tablename__ = "relationship_evidence"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    relationship_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    confidence: Mapped[float] = mapped_column(Float, nullable=False) # The raw LLM extraction confidence
    supporting_text: Mapped[str] = mapped_column(String, nullable=False) # The exact text sentence providing evidence
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True) # E.g., provider, prompt_version
    
    relationship: Mapped["Relationship"] = relationship("Relationship", back_populates="evidence")
