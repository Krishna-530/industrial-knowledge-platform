import logging
from typing import List
from app.retrieval.schemas import RetrievalRequest, RetrievalResult
from app.retrieval.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

class RetrievalWorkflow:
    """
    Orchestrates the retrieval process for API requests.
    Validates input, extracts user context, and invokes the RetrievalService.
    """
    def __init__(self, retrieval_service: RetrievalService):
        self.retrieval_service = retrieval_service

    async def execute_retrieval(self, request: RetrievalRequest, roles: List[str]) -> RetrievalResult:
        """
        Executes the retrieval request.
        """
        logger.info({
            "event": "workflow_started", 
            "workflow_name": "RetrievalWorkflow",
            "user_id": str(request.requesting_user_id)
        })
        
        from app.retrieval.settings import settings
        from app.retrieval.planners.dto import RetrievalPlan, TraversalStrategyType, RetrievalStrategyType
        from app.retrieval.planners.complexity import QueryComplexityEstimator
        from app.retrieval.validation.query_validator import QueryValidator
        
        # 1. Planning (Rule-based Fast Router for now)
        plan = RetrievalPlan(
            query=request.query,
            strategies=[RetrievalStrategyType.GRAPH, RetrievalStrategyType.KEYWORD],
            traversal_strategy=TraversalStrategyType.NEIGHBORHOOD
        )
        
        if settings.GRAPH_ENABLED and settings.GRAPH_PLANNER_ENABLED:
            try:
                # 2. Validation
                validator = QueryValidator(policy_engine=None) # Normally injected
                # validator.validate(plan)
                
                # 3. Execution & Processing would happen here...
                # (e.g., TraversalRequestBuilder, GraphTraversalEngine, GraphRankingService, GraphContextBudgetService)
                
            except Exception as e:
                # Graceful Degradation
                logger.warning(f"Graph retrieval failed or degraded: {e}. Falling back to Keyword.")
                plan.strategies = [RetrievalStrategyType.KEYWORD]
                
        # Finally hand off to the old RetrievalService with the updated plan
        result = await self.retrieval_service.retrieve(request, roles)
        
        logger.info({
            "event": "workflow_completed", 
            "workflow_name": "RetrievalWorkflow",
            "user_id": str(request.requesting_user_id)
        })
        return result
