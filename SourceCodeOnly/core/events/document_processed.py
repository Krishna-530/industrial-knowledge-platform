from uuid import UUID
from pydantic import BaseModel

class DocumentProcessed(BaseModel):
    """
    Event emitted when a document's content has been fully extracted and saved.
    This acts as the trigger for background indexing.
    """
    document_id: UUID
    document_version_id: UUID
    version_number: int
