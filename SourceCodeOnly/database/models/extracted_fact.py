import uuid
from sqlalchemy import String, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import enum
from database.models.base import Base, TimestampMixin

class FactStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    STALE = "STALE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"

class ExtractedFact(TimestampMixin, Base):
    __tablename__ = "extracted_facts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False) # Not strict FK if chunks aren't in same DB schema, but typical.
    asset_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    property: Mapped[str] = mapped_column(String, nullable=False, index=True)
    value: Mapped[str] = mapped_column(String, nullable=False)
    
    start_offset: Mapped[int] = mapped_column(Integer, nullable=True)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=True)
    
    extraction_model: Mapped[str] = mapped_column(String, nullable=False)
    extraction_version: Mapped[str] = mapped_column(String, nullable=False)
    
    status: Mapped[FactStatus] = mapped_column(SQLEnum(FactStatus, name="fact_status_enum", create_type=False), nullable=False, default=FactStatus.ACTIVE)
