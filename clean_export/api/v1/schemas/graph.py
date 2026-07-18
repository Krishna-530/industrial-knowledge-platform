from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class GraphNodeResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    labels: List[str] = Field(..., description="Node labels in Neo4j")
    properties: Dict[str, Any] = Field(..., description="Key-value properties of the node")

class GraphEdgeResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the edge")
    start_node_id: str = Field(..., description="ID of the source node")
    end_node_id: str = Field(..., description="ID of the target node")
    type: str = Field(..., description="Relationship type")
    properties: Dict[str, Any] = Field(..., description="Edge properties")
    provenance: Optional[Dict[str, Any]] = Field(None, description="Traceability data")

class GraphSearchRequest(BaseModel):
    query: str = Field(..., description="Text query to match nodes/labels")
    limit: int = Field(50, description="Max number of nodes to return")

class GraphSearchResponse(BaseModel):
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]

class NeighborhoodResponse(BaseModel):
    center_node: GraphNodeResponse
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]

class GraphStatisticsResponse(BaseModel):
    total_nodes: int = 0
    total_edges: int = 0
    lag_seconds: float = 0.0
    active_tenants: int = 0
