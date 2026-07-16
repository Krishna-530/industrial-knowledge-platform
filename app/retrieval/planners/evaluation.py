import logging
from app.retrieval.session import RetrievalSession

logger = logging.getLogger(__name__)

class PlannerEvaluationService:
    """
    Continuously evaluates Planner assumptions (Complexity Estimates) vs Actual Execution Data.
    Used for feedback loops and prompt optimization.
    """
    
    @staticmethod
    def evaluate(session: RetrievalSession) -> None:
        if not session.plan or not session.plan.estimated_complexity:
            return
            
        estimate = session.plan.estimated_complexity
        
        # In a real system, we capture actual node/edge expansions from the Traversal Engine
        actual_latency = session.execution_timings.get("GRAPH_EXECUTION", 0.0)
        
        latency_variance = actual_latency - estimate.expected_cost_ms
        
        logger.info(
            f"Planner Evaluation [{session.request_id}] | "
            f"Estimated Latency: {estimate.expected_cost_ms}ms | Actual: {actual_latency:.2f}ms | Variance: {latency_variance:.2f}ms"
        )
        
        # Example condition for telemetry alerts:
        if latency_variance > 1000:
            logger.warning(f"Planner vastly underestimated traversal latency for query: '{session.original_query}'")
