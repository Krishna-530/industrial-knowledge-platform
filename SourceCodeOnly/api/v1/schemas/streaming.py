from pydantic import BaseModel
from typing import Optional, Generic, TypeVar
from uuid import UUID

T = TypeVar('T')

class SseEvent(BaseModel, Generic[T]):
    stream_id: str
    id: str
    event: str
    data: T
    retry: Optional[int] = None

class ConversationStartedEvent(BaseModel):
    conversation_id: UUID

class AssistantDeltaEvent(BaseModel):
    text: str

class ToolStartedEvent(BaseModel):
    tool_name: str
    tool_id: str

class ToolProgressEvent(BaseModel):
    tool_id: str
    message: str

class ToolCompletedEvent(BaseModel):
    tool_id: str
    summary: str

class CitationEvent(BaseModel):
    document_id: UUID
    title: str
    snippet: str

class ErrorEvent(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ConversationCompletedEvent(BaseModel):
    conversation_id: UUID
    assistant_message_id: UUID
    usage: TokenUsage
    finish_reason: str
    latency_ms: int
    tool_count: int

class HeartbeatEvent(BaseModel):
    pass
