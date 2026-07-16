from typing import Any, Dict
from pydantic import BaseModel

class DomainEvent(BaseModel):
    event_type: str
    payload: Dict[str, Any]

class MessageCreatedEvent(DomainEvent):
    event_type: str = "MessageCreated"

class ConversationCompletedEvent(DomainEvent):
    event_type: str = "ConversationCompleted"

class ConversationSummaryRequested(DomainEvent):
    event_type: str = "ConversationSummaryRequested"

class EventDispatcher:
    def __init__(self):
        self._handlers = []

    def register(self, handler):
        self._handlers.append(handler)

    async def dispatch(self, event: DomainEvent):
        for handler in self._handlers:
            await handler(event)
