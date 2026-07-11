from typing import Any, Dict
from app.tools.interfaces.abstract_tool import AbstractTool
from app.tools.models.tool_context import ToolContext
from app.tools.models.knowledge_search_result import KnowledgeSearchResult
from app.workflows.retrieval_workflow import RetrievalWorkflow

class KnowledgeSearchTool(AbstractTool):
    def __init__(self, retrieval_workflow: RetrievalWorkflow):
        self.retrieval_workflow = retrieval_workflow
        
    async def execute(self, arguments: Dict[str, Any], context: ToolContext) -> Any:
        query = arguments.get("query")
        if not query:
            raise ValueError("Missing 'query' argument")
            
        # 1. Execute retrieval
        # Pass workspace_id to ensure tenant isolation
        # Note: In actual phase 6 integration, we'd pass this via context to retrieval workflow
        chunks = await self.retrieval_workflow.execute(query=query) 
        
        # 2. Map to domain result
        result = KnowledgeSearchResult(
            chunks=chunks,
            citations=[], # Gathered from chunks if available
            retrieval_metadata={"query": query, "total_results": len(chunks)}
        )
        
        return result
