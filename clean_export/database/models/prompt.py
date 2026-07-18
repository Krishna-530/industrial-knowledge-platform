import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.models.base import Base, TimestampMixin
import enum

class PromptStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    TESTING = "TESTING"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"

class PromptVersion(TimestampMixin, Base):
    """
    Registry for Prompt Versions to guarantee governance and eliminate prompt drift.
    """
    __tablename__ = "prompt_versions"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True) # e.g. "entity_extraction"
    version: Mapped[str] = mapped_column(String, nullable=False) # e.g. "v1.0.0"
    
    system_prompt: Mapped[str] = mapped_column(String, nullable=False)
    developer_prompt: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    schema_version: Mapped[str] = mapped_column(String, nullable=False)
    
    status: Mapped[PromptStatus] = mapped_column(SQLEnum(PromptStatus), nullable=False, default=PromptStatus.DRAFT, index=True)
    checksum: Mapped[str] = mapped_column(String, nullable=False) # MD5 of prompt content for tamper detection
    
    model_constraints: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True) # {"allowed_models": ["gpt-4o-2024-05-13"]}
