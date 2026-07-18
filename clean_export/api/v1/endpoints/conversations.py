import asyncio
import uuid
import logging
import time
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.security.context import SecurityContext
from dependencies.auth import get_security_context
from api.v1.schemas.conversation import (
    ConversationMessageRequest, ConversationCreateRequest, 
    ConversationResponse, ConversationListResponse
)
from api.v1.schemas.streaming import SseEvent, HeartbeatEvent
from app.workflows.executors.conversation_turn_executor import ConversationTurnExecutor
from core.cancellation import CancellationToken

# Assume a provider for ConversationTurnExecutor exists in a real app
from api.v1.dependencies.conversation import provide_conversation_turn_executor
from app.conversation.conversation_service import ConversationService
from api.v1.dependencies.conversation import provide_conversation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    req: ConversationCreateRequest,
    context: SecurityContext = Depends(get_security_context),
    service: ConversationService = Depends(provide_conversation_service)
):
    # Mock implementation for CRUD
    pass

@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    context: SecurityContext = Depends(get_security_context),
    service: ConversationService = Depends(provide_conversation_service)
):
    # Mock implementation
    pass

@router.get("/{id}", response_model=ConversationResponse)
async def get_conversation(
    id: str,
    context: SecurityContext = Depends(get_security_context),
    service: ConversationService = Depends(provide_conversation_service)
):
    pass

@router.delete("/{id}")
async def delete_conversation(
    id: str,
    context: SecurityContext = Depends(get_security_context),
    service: ConversationService = Depends(provide_conversation_service)
):
    pass

async def _sse_generator(
    executor: ConversationTurnExecutor,
    conversation_id: str,
    message: str,
    cancellation_token: CancellationToken,
    request: Request,
    context: SecurityContext
):
    stream_id = str(uuid.uuid4())
    user_msg_id = str(uuid.uuid4()) # In real app, persist message first
    expected_version = 1
    start_time = time.time()
    
    logger.info(
        "StreamStarted",
        extra={
            "stream_id": stream_id,
            "conversation_id": conversation_id,
            "user_id": str(context.user.id),
            "workspace_id": str(context.workspace_id) if hasattr(context, "workspace_id") else None
        }
    )
    
    async def heartbeat_task():
        try:
            while True:
                await asyncio.sleep(20)
                hb = SseEvent(
                    stream_id=stream_id,
                    id=str(uuid.uuid4()),
                    event="heartbeat",
                    data=HeartbeatEvent()
                )
                # Note: sending heartbeat directly here requires a queue or modifying the generator.
                # For simplicity in this architectural stub, we rely on the main loop.
        except asyncio.CancelledError:
            pass

    # A real implementation would multiplex the executor and heartbeat
    
    try:
        async for event in executor.execute_turn_stream(
            conversation_id=conversation_id,
            user_message_id=user_msg_id,
            expected_version=expected_version,
            cancellation_token=cancellation_token
        ):
            if await request.is_disconnected():
                cancellation_token.cancel()
                break
                
            sse = SseEvent(
                stream_id=stream_id,
                id=str(uuid.uuid4()),
                event=event.__class__.__name__,
                data=event
            )
            
            # Format as SSE
            yield f"id: {sse.id}\nevent: {sse.event}\ndata: {sse.model_dump_json()}\n\n"
            
    except asyncio.CancelledError:
        cancellation_token.cancel()
        logger.warning(
            "StreamCancelled",
            extra={
                "stream_id": stream_id,
                "conversation_id": conversation_id,
                "reason": "asyncio.CancelledError"
            }
        )
    except Exception as e:
        cancellation_token.cancel()
        logger.error(
            "StreamError",
            extra={
                "stream_id": stream_id,
                "conversation_id": conversation_id,
                "error": str(e)
            }
        )
        raise
    finally:
        # Graceful Stream Cleanup
        if not cancellation_token.is_cancelled:
            cancellation_token.cancel()
            
        latency_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "StreamCompleted",
            extra={
                "stream_id": stream_id,
                "conversation_id": conversation_id,
                "finish_reason": "completed_or_cleaned_up",
                "latency_ms": latency_ms
            }
        )

@router.post("/{id}/messages")
async def send_message(
    id: str,
    req: ConversationMessageRequest,
    request: Request,
    context: SecurityContext = Depends(get_security_context),
    executor: ConversationTurnExecutor = Depends(provide_conversation_turn_executor)
):
    cancellation_token = CancellationToken()
    
    return StreamingResponse(
        _sse_generator(executor, id, req.message, cancellation_token, request, context),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
