from typing import Optional, Dict
from app.conversation.models.conversation import Conversation
from core.exceptions.processing import ProcessingFailedException

class ConcurrentUpdateError(ProcessingFailedException):
    def __init__(self, message: str = "Concurrent update detected."):
        super().__init__(message)

class ConversationRepository:
    def __init__(self):
        self._db: Dict[str, Conversation] = {}

    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        return self._db.get(conversation_id)

    async def create(self, conversation: Conversation) -> Conversation:
        self._db[conversation.id] = conversation
        return conversation

    async def update_versioned(self, conversation: Conversation, expected_version: int) -> Conversation:
        existing = self._db.get(conversation.id)
        if not existing:
            raise ProcessingFailedException("Conversation not found")
            
        if existing.version != expected_version:
            raise ConcurrentUpdateError(f"Version mismatch. Expected {expected_version}, got {existing.version}")
            
        conversation.version += 1
        self._db[conversation.id] = conversation
        return conversation
