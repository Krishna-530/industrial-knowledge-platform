from typing import List, Dict
from app.conversation.models.message import Message

class MessageRepository:
    def __init__(self):
        self._db: Dict[str, Message] = {}

    async def create(self, message: Message) -> Message:
        self._db[message.id] = message
        return message

    async def get_by_conversation(self, conversation_id: str) -> List[Message]:
        messages = [m for m in self._db.values() if m.conversation_id == conversation_id]
        messages.sort(key=lambda m: m.sequence_number)
        return messages
        
    async def get_latest_sequence(self, conversation_id: str) -> int:
        messages = [m for m in self._db.values() if m.conversation_id == conversation_id]
        if not messages:
            return 0
        return max(m.sequence_number for m in messages)
