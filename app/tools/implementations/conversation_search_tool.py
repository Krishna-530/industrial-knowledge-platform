from typing import Any, Dict
from app.tools.interfaces.abstract_tool import AbstractTool
from app.tools.models.tool_context import ToolContext
from app.search.strategies.conversation_search_strategy import ConversationSearchStrategy
from app.conversation.conversation_service import ConversationService
from core.exceptions.auth import ForbiddenError

class ConversationSearchTool(AbstractTool):
    def __init__(self, search_strategy: ConversationSearchStrategy, conversation_service: ConversationService):
        self.search_strategy = search_strategy
        self.conversation_service = conversation_service
        
    async def execute(self, arguments: Dict[str, Any], context: ToolContext) -> Any:
        query = arguments.get("query")
        limit = arguments.get("limit", 10)
        
        if not query:
            raise ValueError("Missing 'query' argument")
            
        # Verify access to the conversation context
        conv = await self.conversation_service.get_conversation(context.conversation_id)
        if conv and conv.workspace_id != context.workspace_id:
             raise ForbiddenError("Access denied to search conversation")
            
        # Delegate to search strategy abstraction
        messages = await self.search_strategy.search(
            query=query, 
            conversation_id=context.conversation_id, 
            limit=limit
        )
        
        return [m.model_dump() for m in messages]
