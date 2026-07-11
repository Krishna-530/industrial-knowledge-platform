from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from app.conversation.models.conversation_state import ConversationState
from app.conversation.models.message import Message

class ConversationBase(BaseModel):
    title: str = "New Conversation"
    workspace_id: str
    user_id: str

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    state: ConversationState = ConversationState.CREATED
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
