import uuid
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from database.models.base import Base, TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
