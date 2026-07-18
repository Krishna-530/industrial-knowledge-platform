from pydantic import BaseModel
from uuid import UUID

class ProcessingJobPayload(BaseModel):
    document_id: UUID
    version_id: UUID
    version_number: int
    storage_identifier: str
    mime_type: str

class IndexingJobPayload(BaseModel):
    document_id: UUID
    version_id: UUID
    version_number: int
