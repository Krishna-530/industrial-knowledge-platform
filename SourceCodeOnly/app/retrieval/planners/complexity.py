import logging
from app.retrieval.planners.dto import RetrievalPlan, QueryComplexityEstimate, TraversalStrategyType

logger = logging.getLogger(__name__)

class QueryComplexityEstimator:
    """
    Estimates the computational cost of a graph traversal BEFORE execution.
    """
    
    @staticmethod
    def estimate_complexity(plan: RetrievalPlan, max_depth: int, max_branching_factor: int) -> QueryComplexityEstimate:
        """
        Projects worst-case node and edge expansions based on depth and branching bounds.
        """
        if plan.traversal_strategy == TraversalStrategyType.NEIGHBORHOOD:
            # Worst-case geometric expansion
            nodes = sum(max_branching_factor ** d for d in range(1, max_depth + 1))
            edges = nodes * max_branching_factor # Rough estimate
        elif plan.traversal_strategy == TraversalStrategyType.SHORTEST_PATH:
            # Much narrower search space
            nodes = max_depth * 2
            edges = max_depth * 3
        else:
            nodes = max_branching_factor * max_depth
            edges = max_branching_factor * max_depth * 2

        # Basic linear estimation models
        cost_ms = (nodes * 2) + (edges * 1) # Assumes 2ms per node fetch, 1ms per edge fetch in Neo4j overhead
        tokens = (nodes * 50) + (edges * 150) # Rough string length estimates translated to tokens

        estimate = QueryComplexityEstimate(
            expected_nodes=nodes,
            expected_edges=edges,
            expected_cost_ms=cost_ms,
            expected_tokens=tokens
        )
        
        logger.debug(f"Complexity Estimate for query '{plan.query}': {estimate}")
        return estimate
