from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class DocumentUploaded:
    document_id: UUID
    version_id: UUID
    version_number: int
    storage_identifier: str
    mime_type: str
