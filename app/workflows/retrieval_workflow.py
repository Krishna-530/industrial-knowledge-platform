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
        
        result = await self.retrieval_service.retrieve(request, roles)
        
        logger.info({
            "event": "workflow_completed", 
            "workflow_name": "RetrievalWorkflow",
            "user_id": str(request.requesting_user_id)
        })
        return result
