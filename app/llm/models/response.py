from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

class FinishReason(str, Enum):
    STOP = "stop"
    LENGTH = "length"
    TOOL_CALL = "tool_call"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"

class ToolCallRequest(BaseModel):
    id: str
    name: str
    arguments: str # JSON string representing kwargs

class UsageMetrics(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ProviderMetadata(BaseModel):
    provider_name: str
    model_name: str
    latency_ms: float

class ExecutionResult(BaseModel):
    """
    Normalized result passed up to the LLMWorkflow.
    """
    id: str
    content: str
    tool_calls: List[ToolCallRequest] = []
    finish_reason: FinishReason
    usage: UsageMetrics = UsageMetrics()
    metadata: ProviderMetadata

class StreamChunk(BaseModel):
    """
    Normalized chunk for streaming.
    """
    id: str
    content_delta: str
    tool_call_delta: Optional[ToolCallRequest] = None
    finish_reason: Optional[FinishReason] = None
