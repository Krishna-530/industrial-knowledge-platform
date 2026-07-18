import logging
from app.retrieval.planners.dto import RetrievalPlan
from app.retrieval.policy_engine import RetrievalPolicyEngine

logger = logging.getLogger(__name__)

class InvalidRetrievalPlanError(Exception):
    pass

class QueryValidator:
    """
    Validates a RetrievalPlan before it reaches the execution engines.
    Prevents excessively expensive or malformed queries.
    """
    def __init__(self, policy_engine: RetrievalPolicyEngine):
        self.policy = policy_engine.get_policy()

    def validate(self, plan: RetrievalPlan) -> None:
        logger.info(f"Validating RetrievalPlan for query: '{plan.query}'")
        
        if not plan.strategies:
            raise InvalidRetrievalPlanError("RetrievalPlan must contain at least one strategy.")
            
        if plan.budget_tokens > self.policy.max_tokens:
            raise InvalidRetrievalPlanError(f"Plan budget {plan.budget_tokens} exceeds policy max {self.policy.max_tokens}.")
            
        if plan.estimated_complexity:
            if plan.estimated_complexity.expected_nodes > self.policy.max_nodes_traversed:
                raise InvalidRetrievalPlanError(f"Expected nodes {plan.estimated_complexity.expected_nodes} exceeds max {self.policy.max_nodes_traversed}.")
                
            if plan.estimated_complexity.expected_cost_ms > self.policy.planner_timeout_ms:
                raise InvalidRetrievalPlanError(f"Expected latency {plan.estimated_complexity.expected_cost_ms}ms exceeds timeout {self.policy.planner_timeout_ms}ms.")

        logger.debug("RetrievalPlan validated successfully.")
