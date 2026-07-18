from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime
from app.prompt.models.template import PromptVersion

class PromptAudit(BaseModel):
    template_id: UUID
    template_version: PromptVersion
    variables_used: List[str]
    prompt_hash: str
    generation_timestamp: datetime
    tracking_id: UUID
