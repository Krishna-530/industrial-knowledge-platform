from pydantic import BaseModel
from uuid import UUID
from app.prompt.models.template import PromptVersion

class PromptConfig(BaseModel):
    language: str
    template_id: UUID
    template_version: PromptVersion
    include_context: bool
    include_history: bool
    include_tools: bool
    verbosity: str
    reasoning_mode: bool
    response_style: str
