from typing import AsyncGenerator, Any
from app.conversation.conversation_service import ConversationService
from app.workflows.executors.conversation_turn_executor import ConversationTurnExecutor
from app.conversation.models.message import MessageCreate
from core.exceptions.processing import ProcessingFailedException

class IdempotencyKeyError(ProcessingFailedException):
    pass

class ConversationWorkflow:
    def __init__(
        self,
        conversation_service: ConversationService,
        turn_executor: ConversationTurnExecutor
    ):
        self.conversation_service = conversation_service
        self.turn_executor = turn_executor
        
        # Simple in-memory idempotency check for phase 7.3
        self._processed_keys = set()

    async def execute_turn_stream(
        self, 
        conversation_id: str, 
        message_data: MessageCreate, 
        expected_version: int,
        idempotency_key: str
    ) -> AsyncGenerator[Any, None]:
        
        # 1. Idempotency Check
        if idempotency_key in self._processed_keys:
            raise IdempotencyKeyError(f"Duplicate request with idempotency key: {idempotency_key}")
            
        self._processed_keys.add(idempotency_key)
        
        # 2. Add User Message
        try:
            user_msg = await self.conversation_service.add_message(
                conversation_id, message_data, expected_version
            )
            expected_version += 1
        except Exception as e:
            self._processed_keys.remove(idempotency_key)
            raise e
            
        # 3. Delegate to Turn Executor
        return self.turn_executor.execute_turn_stream(
            conversation_id=conversation_id,
            user_message_id=user_msg.id,
            expected_version=expected_version
        )
