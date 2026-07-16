from typing import List
import uuid
from datetime import datetime

from app.prompt.models.schemas import PromptMessage, PromptPayload
from app.prompt.models.metadata import PromptMetadata
from app.prompt.models.tools import ToolDefinition
from app.prompt.models.template import PromptTemplate

class PromptBuilder:
    """
    Constructs the final PromptPayload.
    Does not render or select templates.
    """
    def __init__(self):
        self._messages: List[PromptMessage] = []
        self._tools: List[ToolDefinition] = []
        
    def add_message(self, message: PromptMessage) -> 'PromptBuilder':
        self._messages.append(message)
        return self
        
    def add_messages(self, messages: List[PromptMessage]) -> 'PromptBuilder':
        self._messages.extend(messages)
        return self
        
    def add_tool(self, tool: ToolDefinition) -> 'PromptBuilder':
        self._tools.append(tool)
        return self
        
    def build(self, template: PromptTemplate, language: str, renderer_name: str, duration_ms: float) -> PromptPayload:
        metadata = PromptMetadata(
            template_id=template.id,
            template_version=template.version,
            tracking_id=uuid.uuid4(),
            language=language,
            created_at=datetime.utcnow(),
            renderer_name=renderer_name,
            estimated_tokens=0, # Computed by LLM or token counter later
            context_version=None,
            assembly_duration_ms=duration_ms
        )
        
        return PromptPayload(
            messages=self._messages,
            available_tools=self._tools,
            metadata=metadata
        )
