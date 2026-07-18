import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from database.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from database.models.document import Document

class Category(TimestampMixin, Base):
    __tablename__ = "categories"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="category",
        lazy="selectin"
    )
