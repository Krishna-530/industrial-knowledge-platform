from fastapi import APIRouter, Depends, HTTPException, Security
from typing import Dict, Any

from api.v1.schemas.graph import GraphNodeResponse, GraphSearchRequest, GraphSearchResponse, NeighborhoodResponse, GraphStatisticsResponse
from api.v1.schemas.explainability import EvidenceResponse
from dependencies.auth import get_current_user
from app.services.graph_query_service import GraphQueryService
from database.repositories.graph_readonly_repository import ReadOnlyGraphRepository

# Note: In a real enterprise system, dependencies would be injected via a unified dependency provider.
# For this phase, we mock the driver injection for the route dependencies.
router = APIRouter(prefix="/graph", tags=["Graph Explorer"])

def get_graph_query_service() -> GraphQueryService:
    # Stub: driver should be yielded from app state pool
    return GraphQueryService(ReadOnlyGraphRepository(driver=None))

@router.get("/node/{id}", response_model=GraphNodeResponse)
async def get_node(
    id: str,
    user=Security(get_current_user),
    service: GraphQueryService = Depends(get_graph_query_service)
):
    node = await service.get_node(id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.get("/neighborhood/{id}", response_model=NeighborhoodResponse)
async def get_neighborhood(
    id: str,
    depth: int = 1,
    user=Security(get_current_user),
    service: GraphQueryService = Depends(get_graph_query_service)
):
    return await service.get_neighborhood(id, depth)

@router.post("/search", response_model=GraphSearchResponse)
async def search_graph(
    request: GraphSearchRequest,
    user=Security(get_current_user),
    service: GraphQueryService = Depends(get_graph_query_service)
):
    return await service.search_nodes(request.query, request.limit)

@router.get("/statistics", response_model=GraphStatisticsResponse)
async def get_statistics(
    user=Security(get_current_user),
    service: GraphQueryService = Depends(get_graph_query_service)
):
    return await service.get_statistics()

@router.get("/evidence/{relationship_id}", response_model=EvidenceResponse)
async def get_evidence(
    relationship_id: str,
    user=Security(get_current_user),
    service: GraphQueryService = Depends(get_graph_query_service)
):
    return await service.get_relationship_evidence(relationship_id)
