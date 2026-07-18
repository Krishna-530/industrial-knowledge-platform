from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from app.prompt.models.metadata import PromptMetadata
from app.prompt.models.tools import ToolDefinition

class PromptRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    CONTEXT = "context"

class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"

class ContentBlock(BaseModel):
    """Polymorphic base for content blocks"""
    type: ContentType

class TextBlock(ContentBlock):
    type: ContentType = ContentType.TEXT
    text: str

class ImageBlock(ContentBlock):
    type: ContentType = ContentType.IMAGE
    image_url: str
    detail: Optional[str] = "auto"

class PromptMessage(BaseModel):
    role: PromptRole
    content: List[Union[TextBlock, ImageBlock, ContentBlock]]
    name: Optional[str] = None # Used for tool calls

class PromptPayload(BaseModel):
    messages: List[PromptMessage]
    available_tools: List[ToolDefinition] = Field(default_factory=list)
    metadata: PromptMetadata
