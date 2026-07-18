import uuid
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.document import Document
from sqlalchemy import String, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from database.models.base import Base, TimestampMixin

document_tags = Table(
    "document_tags",
    Base.metadata,
    Column("document_id", UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)

class Tag(TimestampMixin, Base):
    __tablename__ = "tags"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    documents: Mapped[List["Document"]] = relationship(
        "Document",
        secondary=document_tags,
        back_populates="tags",
        lazy="selectin"
    )
