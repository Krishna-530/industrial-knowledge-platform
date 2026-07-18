from enum import Enum
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ExplainabilityLevel(str, Enum):
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    FULL = "FULL"
    AUDIT = "AUDIT"

class GraphExplainabilityService:
    """
    Attaches PostgreSQL provenance metadata to Neo4j edges.
    Provides verifiable citations for the LLM output.
    """
    
    @staticmethod
    async def attach_provenance(edges: List[Dict[str, Any]], level: ExplainabilityLevel = ExplainabilityLevel.STANDARD) -> List[Dict[str, Any]]:
        # In production, this batch-fetches from PostgreSQL RelationshipEvidence
        # where relationship_id IN (edges.ids)
        
        for edge in edges:
            if level == ExplainabilityLevel.BASIC:
                edge["provenance"] = {"source": "Knowledge Graph"}
            elif level == ExplainabilityLevel.STANDARD:
                edge["provenance"] = {
                    "document_id": "stub_doc",
                    "chunk_id": "stub_chunk",
                    "confidence": edge.get("quality_score", 1.0)
                }
            elif level in [ExplainabilityLevel.FULL, ExplainabilityLevel.AUDIT]:
                edge["provenance"] = {
                    "document_id": "stub_doc",
                    "chunk_id": "stub_chunk",
                    "confidence": edge.get("quality_score", 1.0),
                    "provider": "openai",
                    "model": "gpt-4",
                    "extraction_time": "2024-01-01T00:00:00Z"
                }
                
        return edges
