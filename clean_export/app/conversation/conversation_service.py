from typing import Optional, List
from app.conversation.models.conversation import Conversation, ConversationCreate
from app.conversation.models.message import Message, MessageCreate
from app.conversation.repositories.conversation_repository import ConversationRepository
from app.conversation.repositories.message_repository import MessageRepository
from app.conversation.repositories.conversation_turn_repository import ConversationTurnRepository
from app.conversation.events.events import EventDispatcher, MessageCreatedEvent

class ConversationService:
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        turn_repo: ConversationTurnRepository,
        event_dispatcher: EventDispatcher
    ):
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.turn_repo = turn_repo
        self.event_dispatcher = event_dispatcher

    async def create_conversation(self, data: ConversationCreate) -> Conversation:
        conversation = Conversation(**data.model_dump())
        return await self.conversation_repo.create(conversation)

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return await self.conversation_repo.get_by_id(conversation_id)
        
    async def get_messages(self, conversation_id: str) -> List[Message]:
        return await self.message_repo.get_by_conversation(conversation_id)

    async def add_message(self, conversation_id: str, data: MessageCreate, expected_version: int) -> Message:
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        
        latest_seq = await self.message_repo.get_latest_sequence(conversation_id)
        
        message = Message(
            conversation_id=conversation_id,
            sequence_number=latest_seq + 1,
            **data.model_dump()
        )
        
        await self.message_repo.create(message)
        
        # Optimistic locking update
        await self.conversation_repo.update_versioned(conversation, expected_version)
        
        await self.event_dispatcher.dispatch(MessageCreatedEvent(payload={"message_id": message.id}))
        
        return message

    async def update_summary(self, conversation: Conversation, expected_version: int) -> Conversation:
        # Optimistic locking update, but we also increment the summary version
        conversation.summary_version += 1
        return await self.conversation_repo.update_versioned(conversation, expected_version)
