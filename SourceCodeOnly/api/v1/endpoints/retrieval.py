from fastapi import APIRouter, Depends, Security
from typing import Optional
from pydantic import BaseModel, Field

from app.search.schemas import SearchQuery
from app.retrieval.schemas import RetrievalRequest, RetrievalResult
from app.workflows.retrieval_workflow import RetrievalWorkflow
from api.v1.dependencies.retrieval import provide_retrieval_workflow
from dependencies.auth import get_current_user

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])

class APIRetrievalRequest(BaseModel):
    search_query: SearchQuery
    latest_only: bool = True
    include_metadata: bool = True
    include_content: bool = True
    max_documents: Optional[int] = Field(None)
    max_content_length: Optional[int] = Field(None)

@router.post("", response_model=RetrievalResult)
async def retrieve_knowledge(
    payload: APIRetrievalRequest,
    current_user = Security(get_current_user),
    workflow: RetrievalWorkflow = Depends(provide_retrieval_workflow)
):
    # Construct full internal request with verified user ID
    request = RetrievalRequest(
        search_query=payload.search_query,
        latest_only=payload.latest_only,
        include_metadata=payload.include_metadata,
        include_content=payload.include_content,
        max_documents=payload.max_documents,
        max_content_length=payload.max_content_length,
        requesting_user_id=current_user.id
    )
    
    # In a real system, current_user.roles or similar would be passed
    roles = getattr(current_user, "roles", [])
    if hasattr(roles, "name"):
        roles = [r.name for r in roles] # if roles are objects
    elif isinstance(roles, list) and len(roles) > 0 and hasattr(roles[0], "name"):
         roles = [r.name for r in roles]
    elif not isinstance(roles, list):
         roles = []

    return await workflow.execute_retrieval(request, roles)

from fastapi.responses import StreamingResponse
import asyncio
import json
from uuid import uuid4
from app.retrieval.session import RetrievalSession
from app.retrieval.orchestrator import GraphRetrievalOrchestrator

@router.post("/stream")
async def stream_knowledge(
    payload: APIRetrievalRequest,
    current_user = Security(get_current_user),
):
    session = RetrievalSession(
        request_id=str(uuid4()),
        tenant_id=getattr(current_user, 'tenant_id', 'default'),
        original_query=payload.search_query.text,
        requesting_user_id=current_user.id
    )
    
    # Stubbed orchestrator dependencies for Stage 3
    orchestrator = GraphRetrievalOrchestrator(None, None, None, None, None)
    
    async def sse_generator():
        yield f"retry: 3000\nid: {session.request_id}\nevent: start\ndata: {json.dumps({'query': payload.search_query.text})}\n\n"
        
        try:
            gen = orchestrator.stream_execute(session)
            while True:
                try:
                    # Wait for next chunk or timeout for heartbeat
                    chunk = await asyncio.wait_for(gen.__anext__(), timeout=15.0)
                    yield f"id: {str(uuid4())}\nevent: message\ndata: {json.dumps(chunk)}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield f"event: heartbeat\ndata: {{}}\n\n"
                except StopAsyncIteration:
                    break
                    
        except asyncio.CancelledError:
            # Client disconnected
            yield f"event: disconnect\ndata: {json.dumps({'status': 'cancelled'})}\n\n"
            raise
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"
            
        yield f"event: complete\ndata: {json.dumps({'status': 'success'})}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
