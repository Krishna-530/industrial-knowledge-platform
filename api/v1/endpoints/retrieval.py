from fastapi import APIRouter, Depends, Security
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.search.schemas import SearchQuery
from app.retrieval.schemas import RetrievalRequest, RetrievalResult
from app.workflows.retrieval_workflow import RetrievalWorkflow
from api.v1.dependencies.retrieval import provide_retrieval_workflow
from api.v1.dependencies.auth import get_current_user

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
