import logging
from typing import List, Dict, Any
from app.retrieval.session import RetrievalSession, RetrievalState
from app.retrieval.processing.query_rewrite import QueryRewriteService
from app.retrieval.budget.adaptive import AdaptiveBudgetAllocator
from app.retrieval.planners.dto import RetrievalStrategyType

logger = logging.getLogger(__name__)

class GraphRetrievalOrchestrator:
    """
    The master coordinator for the 15-stage Retrieval Lifecycle.
    No other service should coordinate the pipeline.
    """
    
    def __init__(self, planner: Any, graph_engine: Any, semantic_engine: Any, keyword_engine: Any, fusion_engine: Any):
        # Engines are injected
        self.planner = planner
        self.graph = graph_engine
        self.semantic = semantic_engine
        self.keyword = keyword_engine
        self.fusion = fusion_engine

    async def execute(self, session: RetrievalSession) -> List[Dict[str, Any]]:
        try:
            # 1. PLANNING & REWRITE
            session.transition(RetrievalState.PLANNING)
            session.rewritten_query = QueryRewriteService.rewrite(session.original_query)
            
            # Plan generation (Stubbed call)
            # session.plan = await self.planner.plan(session.rewritten_query)
            
            # 2. VALIDATION (Skipping stub)
            session.transition(RetrievalState.VALIDATING)
            
            # 3. BUDGET ALLOCATION
            session.transition(RetrievalState.BUDGETING)
            AdaptiveBudgetAllocator.allocate(session, max_tokens=8000)
            
            graph_results, semantic_results, keyword_results = [], [], []
            strategies = [s.value for s in session.plan.strategies] if session.plan else []
            
            # 4. EXECUTION
            if "GRAPH" in strategies:
                session.transition(RetrievalState.GRAPH_EXECUTION)
                # graph_results = await self.graph.execute(...)
                
            if "SEMANTIC" in strategies:
                session.transition(RetrievalState.SEMANTIC_EXECUTION)
                # semantic_results = await self.semantic.execute(...)
                
            if "KEYWORD" in strategies:
                session.transition(RetrievalState.KEYWORD_EXECUTION)
                # keyword_results = await self.keyword.execute(...)
                
            # 5. FUSION
            session.transition(RetrievalState.FUSION)
            fused_results = self.fusion.fuse(graph_results, semantic_results, keyword_results)
            
            # 6. PROMPT BUILDING
            session.transition(RetrievalState.PROMPT_BUILDING)
            # formatted = PromptFormatter.format(fused_results)
            
            session.transition(RetrievalState.COMPLETED)
            return fused_results
            
        except Exception as e:
            logger.error(f"Retrieval Orchestrator failed: {e}")
            session.add_warning(str(e))
            session.transition(RetrievalState.FAILED)
            raise
            
    async def stream_execute(self, session: RetrievalSession):
        """
        Streaming execution yielding results incrementally so the client does not wait 
        for the slowest retrieval source (e.g., Semantic Search).
        """
        try:
            session.transition(RetrievalState.PLANNING)
            session.rewritten_query = QueryRewriteService.rewrite(session.original_query)
            # Stubbed planner and validation...
            
            # Fire keyword first (fastest)
            yield {"source": "KEYWORD", "status": "processing"}
            # keyword_results = await self.keyword.execute(...)
            # yield {"source": "KEYWORD", "results": keyword_results}
            
            # Fire graph next
            yield {"source": "GRAPH", "status": "processing"}
            # graph_results = await self.graph.execute(...)
            # yield {"source": "GRAPH", "results": graph_results}
            
            # Fire semantic last (slowest embedding generation)
            yield {"source": "SEMANTIC", "status": "processing"}
            # semantic_results = await self.semantic.execute(...)
            # yield {"source": "SEMANTIC", "results": semantic_results}
            
            session.transition(RetrievalState.COMPLETED)
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield {"error": str(e)}
