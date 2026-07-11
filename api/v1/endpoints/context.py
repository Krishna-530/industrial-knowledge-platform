from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.search.schemas import SearchQuery
from app.retrieval.schemas import RetrievalRequest
from app.context.schemas import ContextPayload, ContextConfig
from app.workflows.context_workflow import ContextWorkflow
from api.v1.dependencies.context import provide_context_workflow
from api.v1.dependencies.auth import get_current_user

router = APIRouter(prefix="/context", tags=["Context Assembly"])

class APIContextRequest(BaseModel):
    search_query: SearchQuery
    context_config: ContextConfig

@router.post("/assemble", response_model=ContextPayload)
async def assemble_context(
    payload: APIContextRequest,
    current_user = Security(get_current_user),
    workflow: ContextWorkflow = Depends(provide_context_workflow)
):
    # Construct RetrievalRequest mapping
    retrieval_request = RetrievalRequest(
        search_query=payload.search_query,
        latest_only=True,
        include_metadata=True,
        include_content=True,
        max_documents=payload.context_config.max_documents,
        max_content_length=None,
        requesting_user_id=current_user.id
    )
    
    # Extract roles safely
    roles = getattr(current_user, "roles", [])
    if hasattr(roles, "name"):
        roles = [r.name for r in roles]
    elif isinstance(roles, list) and len(roles) > 0 and hasattr(roles[0], "name"):
         roles = [r.name for r in roles]
    elif not isinstance(roles, list):
         roles = []

    return await workflow.execute_assembly(retrieval_request, roles, payload.context_config)
