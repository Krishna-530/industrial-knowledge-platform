from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from app.conversation.models.conversation import ConversationCreate, Conversation
from app.conversation.models.message import MessageCreate
from app.conversation.conversation_service import ConversationService
from app.workflows.conversation_workflow import ConversationWorkflow, IdempotencyKeyError
from api.v1.dependencies.conversation import provide_conversation_service, provide_conversation_workflow

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("", response_model=Conversation)
async def create_conversation(
    data: ConversationCreate,
    service: ConversationService = Depends(provide_conversation_service)
):
    return await service.create_conversation(data)

@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    expected_version: int,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    workflow: ConversationWorkflow = Depends(provide_conversation_workflow)
):
    try:
        # A real implementation would parse the stream chunks into Server-Sent Events
        async def event_generator():
            async for chunk in await workflow.execute_turn_stream(
                conversation_id=conversation_id,
                message_data=data,
                expected_version=expected_version,
                idempotency_key=idempotency_key
            ):
                # Mocking SSE format for chunks
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
        
    except IdempotencyKeyError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
