import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import String, Integer, Enum as SQLEnum, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.models.base import Base, TimestampMixin
from core.enums import GraphOutboxEventType, GraphOutboxEventStatus

class GraphOutboxEvent(TimestampMixin, Base):
    __tablename__ = "graph_outbox_events"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[GraphOutboxEventType] = mapped_column(SQLEnum(GraphOutboxEventType), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    graph_projection_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[GraphOutboxEventStatus] = mapped_column(SQLEnum(GraphOutboxEventStatus), nullable=False, default=GraphOutboxEventStatus.PENDING, index=True)
    
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
