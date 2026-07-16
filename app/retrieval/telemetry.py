import logging
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

class RetrievalTelemetryPayload(BaseModel):
    query: str
    planner_latency_ms: int
    planner_decision: str
    cache_hit: bool
    entity_resolution_ms: int
    ranking_ms: int
    traversal_ms: int
    context_budget_ms: int
    prompt_tokens_saved: int
    discarded_edges: int
    discarded_nodes: int
    error: Optional[str] = None

class RetrievalTelemetryService:
    @staticmethod
    def emit(payload: RetrievalTelemetryPayload) -> None:
        """
        Emits structured logs for telemetry/dashboarding.
        """
        logger.info(
            "Retrieval Telemetry | "
            f"Query: '{payload.query}' | "
            f"Decision: {payload.planner_decision} | "
            f"Traversal Latency: {payload.traversal_ms}ms | "
            f"Saved Tokens: {payload.prompt_tokens_saved} | "
            f"Cache Hit: {payload.cache_hit}"
        )
