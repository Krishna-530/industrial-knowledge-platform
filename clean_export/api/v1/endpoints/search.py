from fastapi import APIRouter, Depends, Query, Security
from typing import List, Optional
from uuid import UUID

from app.search.schemas import SearchQuery, SearchResultPage
from app.workflows.search_workflow import SearchWorkflow
from api.v1.dependencies.search import provide_search_workflow
from dependencies.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("", response_model=SearchResultPage)
async def search_documents(
    q: str = Query(..., min_length=1, description="The search query text"),
    language: str = Query("english", description="The language dictionary to use"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_order: str = Query("relevance", description="relevance, date_desc, date_asc"),
    category_id: Optional[UUID] = Query(None),
    tags: Optional[List[UUID]] = Query(None),
    current_user = Security(get_current_user),
    workflow: SearchWorkflow = Depends(provide_search_workflow)
):
    query = SearchQuery(
        query_text=q,
        language=language,
        limit=limit,
        offset=offset,
        sort_order=sort_order,
        category_id=category_id,
        tags=tags
    )
    return await workflow.execute_search(query)
