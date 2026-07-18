from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from uuid import UUID

class JobResponse(BaseModel):
    id: UUID
    job_type: str
    status: str
    attempts: int
    max_attempts: int
    is_dead_letter: bool
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    last_attempt_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    error_message: Optional[str] = None
    payload: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int

class DocumentStatusInfo(BaseModel):
    id: UUID
    title: str
    status: str
    extraction_status: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class DocumentContentStatusInfo(BaseModel):
    processing_status: Optional[str] = None
    processing_error: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class JobDetailResponse(BaseModel):
    job: JobResponse
    document: Optional[DocumentStatusInfo] = None
    document_content: Optional[DocumentContentStatusInfo] = None

class HealthCheckResult(BaseModel):
    service: str
    status: str
    latency: int
    message: str

class SystemHealthResponse(BaseModel):
    services: List[HealthCheckResult]
    last_checked: datetime
