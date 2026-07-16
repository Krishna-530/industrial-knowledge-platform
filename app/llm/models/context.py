from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import asyncio

class ExecutionContext(BaseModel):
    """
    Immutable tracking context spanning the entire request lifetime.
    """
    request_id: UUID
    trace_id: UUID
    correlation_id: UUID
    deadline: datetime
    cancellation_token: asyncio.Event = Field(default_factory=asyncio.Event)

    class Config:
        arbitrary_types_allowed = True

class ExecutionState(BaseModel):
    """
    Mutable state modified by pipeline stages during execution.
    """
    selected_provider: Optional[str] = None
    selected_model: Optional[str] = None
    retry_count: int = 0
    current_stage: str = "INIT"
    fatal_error: Optional[Exception] = None
    
    class Config:
        arbitrary_types_allowed = True
