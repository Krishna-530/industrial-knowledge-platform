import asyncio
from pydantic import BaseModel, Field

class ToolContext(BaseModel):
    user_id: str
    workspace_id: str
    conversation_id: str
    max_output_length: int = 16384 # Protects LLM context window
    cancellation_token: asyncio.Event = Field(default_factory=asyncio.Event)
    
    class Config:
        arbitrary_types_allowed = True
