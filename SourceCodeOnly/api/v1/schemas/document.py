from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from core.enums import DocumentStatus

class CreateDocumentRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    owner_id: UUID
    category_id: UUID
    tag_ids: List[UUID] = Field(default_factory=list)

class UpdateDocumentRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    owner_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None
    status: Optional[DocumentStatus] = None

class VersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    document_id: UUID
    version_number: int
    storage_identifier: Optional[str]
    checksum: Optional[str]
    uploaded_by: UUID
    created_at: datetime

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    description: Optional[str]
    owner_id: UUID
    category_id: UUID
    current_version: int
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
