from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from uuid import UUID
from datetime import datetime, timezone
import uuid

class BaseTelemetryEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    event_id: UUID
    timestamp: datetime
    request_id: str
    correlation_id: str
    
    @classmethod
    def create_base(cls, request_id: str, correlation_id: str) -> dict[str, Any]:
        return {
            "event_id": uuid.uuid4(),
            "timestamp": datetime.now(timezone.utc),
            "request_id": request_id,
            "correlation_id": correlation_id
        }

class SearchCompletedEvent(BaseTelemetryEvent):
    user_id: UUID
    query: str
    retrieval_strategy: str
    execution_time_ms: float
    result_count: int
    success: bool

class DocumentUploadedEvent(BaseTelemetryEvent):
    document_id: UUID
    uploader_id: UUID
    file_size: int
    mime_type: str

class JobCompletedEvent(BaseTelemetryEvent):
    job_id: UUID
    duration_ms: float
    retry_count: int
    worker_id: str
    status: str

class UserLoggedInEvent(BaseTelemetryEvent):
    user_id: UUID
    authentication_method: str

class DocumentViewedEvent(BaseTelemetryEvent):
    user_id: UUID
    document_id: UUID

class DashboardViewedEvent(BaseTelemetryEvent):
    user_id: UUID
