from typing import List
from app.prompt.models.schemas import PromptMessage, PromptRole

class PromptValidator:
    """
    Validates structural rules of the assembled payload.
    """
    def validate(self, messages: List[PromptMessage]) -> None:
        if not messages:
            raise ValueError("PromptPayload must contain at least one message.")
            
        # Ensure only one SYSTEM message exists if supported by provider norms,
        # or just ensure basic integrity.
        system_msgs = [m for m in messages if m.role == PromptRole.SYSTEM]
        if len(system_msgs) > 1:
            # Not strictly an error for all LLMs, but a warning
            pass
