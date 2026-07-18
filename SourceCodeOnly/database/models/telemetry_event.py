import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base, TimestampMixin

class TelemetryEvent(Base, TimestampMixin):
    __tablename__ = "telemetry_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    request_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    correlation_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True) # e.g., DocumentUploaded, UserLoggedIn, DocumentViewed, DashboardViewed
    
    # Optional generic fields depending on event type
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Store event-specific metadata (file_size, mime_type, auth_method) as JSONB
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
