import logging
from typing import Dict, Any

from app.prompt.models.config import PromptConfig
from app.prompt.models.schemas import PromptPayload
from app.prompt.prompt_service import PromptService
# In a real system, this workflow would depend on ContextWorkflow or RetrievalWorkflow
# to fetch data. For this boundary, it accepts the pre-assembled variables.

logger = logging.getLogger(__name__)

class PromptWorkflow:
    """
    Validates API boundaries and maps inputs into the domain service.
    """
    def __init__(self, prompt_service: PromptService):
        self.prompt_service = prompt_service

    async def execute_assembly(self, config: PromptConfig, variables: Dict[str, Any]) -> PromptPayload:
        """
        Executes Prompt Assembly.
        """
        logger.info({
            "event": "workflow_started", 
            "workflow_name": "PromptWorkflow",
            "template_id": str(config.template_id)
        })
        
        # In a full system, this is where ContextWorkflow would be called
        # if `variables` just contained a "query" and we needed to fetch context.
        
        payload = self.prompt_service.assemble(config, variables)
        
        logger.info({
            "event": "workflow_completed", 
            "workflow_name": "PromptWorkflow",
            "template_id": str(config.template_id)
        })
        
        return payload
