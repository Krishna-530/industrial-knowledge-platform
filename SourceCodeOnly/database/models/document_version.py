import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.document import Document
    from database.models.document_content import DocumentContent

from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from database.models.base import Base

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_identifier: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__('datetime').datetime.now(__import__('datetime').timezone.utc),
        nullable=False
    )

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="versions",
        lazy="selectin"
    )
    
    content: Mapped["DocumentContent"] = relationship(
        "DocumentContent",
        back_populates="document_version",
        lazy="selectin",
        uselist=False,
        cascade="all, delete-orphan"
    )
