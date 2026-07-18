import logging
from app.retrieval.session import RetrievalSession
from app.retrieval.budget.manager import BudgetAllocation

logger = logging.getLogger(__name__)

class AdaptiveBudgetAllocator:
    """
    Dynamically adjusts budget slices based on runtime complexity and planner confidence.
    """
    
    @staticmethod
    def allocate(session: RetrievalSession, max_tokens: int) -> None:
        plan = session.plan
        strategies = plan.strategies if plan else []
        
        if not strategies:
            return
            
        strategy_count = len(strategies)
        # Fast path
        if strategy_count == 1:
            if strategies[0].value == "GRAPH":
                session.graph_budget = max_tokens
            elif strategies[0].value == "KEYWORD":
                session.keyword_budget = max_tokens
            elif strategies[0].value == "SEMANTIC":
                session.semantic_budget = max_tokens
            return

        # Adaptive splitting
        # Graph requires more tokens to express relationships effectively.
        if "GRAPH" in [s.value for s in strategies] and strategy_count == 2:
            session.graph_budget = int(max_tokens * 0.7)
            # The remaining 30% goes to the other strategy
            remaining = int(max_tokens * 0.3)
            if "SEMANTIC" in [s.value for s in strategies]:
                session.semantic_budget = remaining
            else:
                session.keyword_budget = remaining
        else:
            # Fallback equal distribution
            slice_size = max_tokens // strategy_count
            session.graph_budget = slice_size if "GRAPH" in [s.value for s in strategies] else 0
            session.semantic_budget = slice_size if "SEMANTIC" in [s.value for s in strategies] else 0
            session.keyword_budget = slice_size if "KEYWORD" in [s.value for s in strategies] else 0
            
        logger.info(
            f"Adaptive Budget Allocated: Graph={session.graph_budget}, "
            f"Semantic={session.semantic_budget}, Keyword={session.keyword_budget}"
        )
