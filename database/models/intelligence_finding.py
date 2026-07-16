import uuid
from typing import List
from sqlalchemy import String, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum
from database.models.base import Base, TimestampMixin

class FindingType(str, enum.Enum):
    CONFLICT = "CONFLICT"
    CORROBORATION = "CORROBORATION"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"
    MISSING = "MISSING"

class IntelligenceFinding(TimestampMixin, Base):
    __tablename__ = "intelligence_findings"
    
    __table_args__ = (
        UniqueConstraint("asset_id", "property", "type", name="uq_asset_property_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[FindingType] = mapped_column(SQLEnum(FindingType, name="finding_type_enum", create_type=False), nullable=False)
    asset_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    property: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    # Store affected fact IDs for navigation
    affected_fact_ids: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=list)
