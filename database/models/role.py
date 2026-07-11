import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Table, Column, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from database.models.base import Base, TimestampMixin

# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="RESTRICT"), primary_key=True),
    extend_existing=True
)

class Role(TimestampMixin, Base):
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    permissions: Mapped[List["Permission"]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin"
    )

class Permission(Base):
    """Permissions don't need updated_at, but we'll use Base directly."""
    __tablename__ = "permissions"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__('datetime').datetime.now(__import__('datetime').timezone.utc),
        nullable=False
    )

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permissions,
        back_populates="permissions"
    )
