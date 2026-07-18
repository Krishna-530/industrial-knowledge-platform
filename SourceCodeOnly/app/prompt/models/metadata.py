from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.prompt.models.template import PromptVersion

class PromptMetadata(BaseModel):
    template_id: UUID
    template_version: PromptVersion
    tracking_id: UUID
    language: str
    created_at: datetime
    renderer_name: str
    estimated_tokens: int
    context_version: Optional[str]
    assembly_duration_ms: float
