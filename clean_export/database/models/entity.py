import uuid
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.models.base import Base, TimestampMixin
from core.enums import EntityStatus

if TYPE_CHECKING:
    pass

class Entity(TimestampMixin, Base):
    __tablename__ = "entities"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    canonical_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[EntityStatus] = mapped_column(SQLEnum(EntityStatus), nullable=False, default=EntityStatus.ACTIVE, index=True)
    
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    first_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_document_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Graph metrics for GraphRAG readiness
    graph_rank: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pagerank: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    degree: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    centrality: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    frequency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    aliases: Mapped[List["EntityAlias"]] = relationship(
        "EntityAlias",
        back_populates="canonical_entity",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    versions: Mapped[List["EntityVersion"]] = relationship(
        "EntityVersion",
        back_populates="entity",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class EntityAlias(TimestampMixin, Base):
    __tablename__ = "entity_aliases"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    canonical_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    alias_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    canonical_entity: Mapped["Entity"] = relationship(
        "Entity",
        back_populates="aliases",
        lazy="selectin"
    )

class EntityVersion(TimestampMixin, Base):
    __tablename__ = "entity_versions"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_name: Mapped[str] = mapped_column(String, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    entity: Mapped["Entity"] = relationship(
        "Entity",
        back_populates="versions",
        lazy="selectin"
    )
