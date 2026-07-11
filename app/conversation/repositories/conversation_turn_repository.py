from typing import List, Dict, Optional
from app.conversation.models.conversation_turn import ConversationTurn

class ConversationTurnRepository:
    def __init__(self):
        self._db: Dict[str, ConversationTurn] = {}

    async def create(self, turn: ConversationTurn) -> ConversationTurn:
        self._db[turn.id] = turn
        return turn

    async def get_by_conversation(self, conversation_id: str) -> List[ConversationTurn]:
        turns = [t for t in self._db.values() if t.conversation_id == conversation_id]
        # In memory sort by creation time
        turns.sort(key=lambda t: t.created_at)
        return turns
