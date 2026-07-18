from typing import List
from app.prompt.interfaces import AbstractMessageOrderingStrategy
from app.prompt.models.schemas import PromptMessage, PromptRole

class StandardMessageOrderingStrategy(AbstractMessageOrderingStrategy):
    """
    Enforces a strict order:
    1. System messages
    2. Context messages
    3. User/Assistant history
    4. Current User message
    """
    def order(self, messages: List[PromptMessage]) -> List[PromptMessage]:
        system_msgs = [m for m in messages if m.role == PromptRole.SYSTEM]
        context_msgs = [m for m in messages if m.role == PromptRole.CONTEXT]
        history_msgs = [m for m in messages if m.role in (PromptRole.ASSISTANT, PromptRole.USER, PromptRole.TOOL)]
        
        # In a real implementation, we'd distinguish the final user message from history.
        # For simplicity, we just append history after context.
        return system_msgs + context_msgs + history_msgs
