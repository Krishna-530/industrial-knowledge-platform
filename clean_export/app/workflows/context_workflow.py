import logging
from typing import List

from app.retrieval.schemas import RetrievalRequest
from app.context.schemas import ContextConfig, ContextPayload
from app.workflows.retrieval_workflow import RetrievalWorkflow
from app.context.context_service import ContextService

logger = logging.getLogger(__name__)

class ContextWorkflow:
    """
    Validates the HTTP API request, triggers Retrieval to get KnowledgeDocuments, 
    and then passes them through the Context Assembly Engine.
    """
    def __init__(self, retrieval_workflow: RetrievalWorkflow, context_service: ContextService):
        self.retrieval_workflow = retrieval_workflow
        self.context_service = context_service

    async def execute_assembly(self, retrieval_request: RetrievalRequest, roles: List[str], config: ContextConfig) -> ContextPayload:
        """
        Executes Retrieval and then formats the output into a ContextPayload.
        """
        logger.info({
            "event": "workflow_started", 
            "workflow_name": "ContextWorkflow",
            "user_id": str(retrieval_request.requesting_user_id)
        })
        
        # 1. Fetch authorized canonical KnowledgeDocuments
        retrieval_result = await self.retrieval_workflow.execute_retrieval(retrieval_request, roles)
        
        # 2. Assemble Context
        payload = self.context_service.assemble(retrieval_result.items, config)
        
        logger.info({
            "event": "workflow_completed", 
            "workflow_name": "ContextWorkflow",
            "user_id": str(retrieval_request.requesting_user_id)
        })
        
        return payload
