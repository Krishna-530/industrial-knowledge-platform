from enum import Enum

class CypherQueryName(str, Enum):
    GET_NEIGHBORHOOD = "GET_NEIGHBORHOOD"
    GET_SHORTEST_PATH = "GET_SHORTEST_PATH"

class CypherTemplateRegistry:
    """
    Centralized registry of approved, parameterized Cypher queries.
    Prevents ad-hoc Cypher injection vulnerabilities and sprawl.
    """
    
    _templates = {
        CypherQueryName.GET_NEIGHBORHOOD: """
            MATCH (n:Entity {id: $entity_id})-[r*1..$max_depth]-(m)
            WITH r, m LIMIT $max_edges
            RETURN r AS edge, m AS node
        """,
        CypherQueryName.GET_SHORTEST_PATH: """
            MATCH p = shortestPath((start:Entity {id: $start_id})-[*1..$max_depth]-(end:Entity {id: $end_id}))
            RETURN p
        """
    }

    @classmethod
    def get_template(cls, name: CypherQueryName) -> str:
        if name not in cls._templates:
            raise ValueError(f"Cypher template {name} not found in registry.")
        return cls._templates[name]
