from pydantic import BaseModel
from typing import Dict, Any
from app.retrieval.cypher.registry import CypherQueryName, CypherTemplateRegistry
from app.retrieval.policy_engine import RetrievalPolicy

class TraversalRequest(BaseModel):
    query_string: str
    parameters: Dict[str, Any]
    timeout_ms: int

class TraversalRequestBuilder:
    """
    Constructs safe execution payloads by marrying Cypher templates with Policy bounds.
    Prevents the Traversal Engine from making policy decisions.
    """
    def __init__(self, policy: RetrievalPolicy):
        self.policy = policy

    def build_neighborhood_request(self, entity_id: str) -> TraversalRequest:
        template = CypherTemplateRegistry.get_template(CypherQueryName.GET_NEIGHBORHOOD)
        
        # Inject policy constraints securely
        parameters = {
            "entity_id": entity_id,
            "max_depth": self.policy.max_depth,
            "max_edges": self.policy.max_edges_traversed
        }
        
        return TraversalRequest(
            query_string=template,
            parameters=parameters,
            timeout_ms=self.policy.planner_timeout_ms
        )
