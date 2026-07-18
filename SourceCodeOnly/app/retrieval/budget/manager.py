from pydantic import BaseModel
from typing import Dict
from app.retrieval.policy_engine import RetrievalPolicyEngine

class BudgetAllocation(BaseModel):
    keyword_budget: int
    semantic_budget: int
    graph_budget: int

class RetrievalBudgetManager:
    """
    Holistically divides the total available prompt tokens among retrieval strategies.
    Prevents the Graph strategy from starving the Semantic strategy.
    """
    def __init__(self, policy_engine: RetrievalPolicyEngine):
        self.policy = policy_engine.get_policy()

    def allocate(self, total_budget: int, requested_strategies: list[str]) -> BudgetAllocation:
        # Cap to global policy
        budget = min(total_budget, self.policy.max_tokens)
        
        allocation = BudgetAllocation(keyword_budget=0, semantic_budget=0, graph_budget=0)
        
        strategy_count = len(requested_strategies)
        if strategy_count == 0:
            return allocation
            
        # Simplistic equal slice allocation for now.
        # In a real system, GRAPH might get a larger slice due to relationship overhead.
        slice_size = budget // strategy_count
        
        for strategy in requested_strategies:
            if strategy == "KEYWORD":
                allocation.keyword_budget = slice_size
            elif strategy == "SEMANTIC":
                allocation.semantic_budget = slice_size
            elif strategy == "GRAPH":
                allocation.graph_budget = slice_size
                
        return allocation
