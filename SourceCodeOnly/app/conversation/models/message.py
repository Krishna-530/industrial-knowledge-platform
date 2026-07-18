from typing import Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class MessageBase(BaseModel):
    role: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sequence_number: int
    interrupted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
