from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.conversation.models.conversation_state import ConversationState

class ConversationMessageRequest(BaseModel):
    message: str = Field(..., description="The user's message to the assistant")
    workspace_id: Optional[UUID] = None

class ConversationBase(BaseModel):
    title: Optional[str] = None
    workspace_id: Optional[UUID] = None

class ConversationCreateRequest(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: UUID
    state: ConversationState
    created_at: datetime
    updated_at: datetime

class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int
