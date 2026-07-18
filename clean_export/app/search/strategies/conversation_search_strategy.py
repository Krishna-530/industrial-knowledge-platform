from abc import ABC, abstractmethod
from typing import List
from app.conversation.models.message import Message

class ConversationSearchStrategy(ABC):
    @abstractmethod
    async def search(self, query: str, conversation_id: str, limit: int = 10) -> List[Message]:
        pass
        
class SubstringConversationSearchStrategy(ConversationSearchStrategy):
    def __init__(self, message_repo):
        self.message_repo = message_repo
        
    async def search(self, query: str, conversation_id: str, limit: int = 10) -> List[Message]:
        messages = await self.message_repo.get_by_conversation(conversation_id)
        query_lower = query.lower()
        results = [m for m in messages if query_lower in m.content.lower()]
        return results[-limit:]
