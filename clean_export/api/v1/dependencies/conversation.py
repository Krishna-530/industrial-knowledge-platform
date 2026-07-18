from fastapi import Depends
from app.conversation.repositories.conversation_repository import ConversationRepository
from app.conversation.repositories.message_repository import MessageRepository
from app.conversation.repositories.conversation_turn_repository import ConversationTurnRepository
from app.conversation.events.events import EventDispatcher
from app.conversation.conversation_service import ConversationService
from app.workflows.executors.conversation_turn_executor import ConversationTurnExecutor
from app.workflows.conversation_workflow import ConversationWorkflow
from app.conversation.models.conversation_config import ConversationConfig
# Note: In a real wiring, we would import the actual workflows below
# from api.v1.dependencies.workflows import provide_retrieval_workflow, provide_context_workflow, provide_prompt_workflow, provide_llm_workflow

def provide_conversation_config() -> ConversationConfig:
    return ConversationConfig()

def provide_conversation_repo() -> ConversationRepository:
    return ConversationRepository()

def provide_message_repo() -> MessageRepository:
    return MessageRepository()
    
def provide_turn_repo() -> ConversationTurnRepository:
    return ConversationTurnRepository()

def provide_event_dispatcher() -> EventDispatcher:
    return EventDispatcher()

def provide_conversation_service(
    conversation_repo: ConversationRepository = Depends(provide_conversation_repo),
    message_repo: MessageRepository = Depends(provide_message_repo),
    turn_repo: ConversationTurnRepository = Depends(provide_turn_repo),
    event_dispatcher: EventDispatcher = Depends(provide_event_dispatcher)
) -> ConversationService:
    return ConversationService(conversation_repo, message_repo, turn_repo, event_dispatcher)

from app.workflows.tool_workflow import ToolWorkflow
from api.v1.dependencies.tools import provide_tool_workflow

def provide_conversation_turn_executor(
    conversation_service: ConversationService = Depends(provide_conversation_service),
    tool_workflow: ToolWorkflow = Depends(provide_tool_workflow),
    config: ConversationConfig = Depends(provide_conversation_config)
) -> ConversationTurnExecutor:
    # Mocks for the downstream workflows
    retrieval_workflow = None 
    context_workflow = None
    prompt_workflow = None
    llm_workflow = None
    
    return ConversationTurnExecutor(
        conversation_service,
        retrieval_workflow,
        context_workflow,
        prompt_workflow,
        llm_workflow,
        tool_workflow,
        config
    )

def provide_conversation_workflow(
    conversation_service: ConversationService = Depends(provide_conversation_service),
    turn_executor: ConversationTurnExecutor = Depends(provide_conversation_turn_executor)
) -> ConversationWorkflow:
    return ConversationWorkflow(conversation_service, turn_executor)
