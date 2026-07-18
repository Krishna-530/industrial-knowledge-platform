from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class GraphTraversalMetrics(BaseModel):
    nodes_expanded: int = 0
    edges_traversed: int = 0
    pruned_nodes: int = 0
    branch_factor: float = 0.0
    cache_hit: bool = False
    graph_latency_ms: float = 0.0
    context_compression_ratio: float = 1.0

class GraphMetricsService:
    """
    Centralizes telemetry collection for the Traversal Engine.
    """
    
    @staticmethod
    def record_traversal(metrics: GraphTraversalMetrics) -> None:
        logger.info(
            f"Traversal Metrics | Latency: {metrics.graph_latency_ms:.2f}ms | "
            f"Nodes: {metrics.nodes_expanded} | Edges: {metrics.edges_traversed} | "
            f"Pruned: {metrics.pruned_nodes} | Cache Hit: {metrics.cache_hit} | "
            f"Compression: {metrics.context_compression_ratio:.2f}"
        )
        # TODO: Push to Prometheus / Datadog
