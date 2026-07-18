from typing import Any, List, Dict
from pydantic import BaseModel, Field

class ToolCallResult(BaseModel):
    tool_call_id: str
    tool_name: str
    tool_version: str = "1.0.0"
    execution_id: str
    content: str
    is_error: bool = False
    status: str = "SUCCESS"
    truncated: bool = False
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    latency_ms: float = 0.0
