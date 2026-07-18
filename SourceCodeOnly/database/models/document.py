import uuid
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.user import User
    from database.models.category import Category
    from database.models.tag import Tag
    from database.models.document_version import DocumentVersion

from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from database.models.base import Base, TimestampMixin
from core.enums import DocumentStatus, ExtractionStatus

class Document(TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[DocumentStatus] = mapped_column(SQLEnum(DocumentStatus), nullable=False, index=True, default=DocumentStatus.DRAFT)
    extraction_status: Mapped[Optional[ExtractionStatus]] = mapped_column(SQLEnum(ExtractionStatus), nullable=True, index=True)

    owner: Mapped["User"] = relationship(
        "User",
        lazy="selectin"
    )
    
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="documents",
        lazy="selectin"
    )

    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="document_tags",
        back_populates="documents",
        lazy="selectin"
    )

    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
