from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class ConversationTurn(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    user_message_id: str
    assistant_message_id: Optional[str] = None
    latency_ms: float = 0.0
    tool_calls_executed: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
