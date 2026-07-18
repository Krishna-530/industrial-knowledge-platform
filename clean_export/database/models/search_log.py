import uuid
from sqlalchemy import String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from database.models.base import Base, TimestampMixin

class SearchLog(Base, TimestampMixin):
    __tablename__ = "search_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    request_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    correlation_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(String, nullable=False)
    retrieval_strategy: Mapped[str] = mapped_column(String, nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    result_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
