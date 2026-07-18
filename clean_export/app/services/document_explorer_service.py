import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from database.repositories.graph_readonly_repository import ReadOnlyGraphRepository
from api.v1.schemas.explorer import ExplorerChunkResponse, ExplorerEntityResponse, ExplorerRelationshipResponse

logger = logging.getLogger(__name__)

class DocumentExplorerService:
    """
    Service specifically designed for UI read operations on Document details.
    Leverages the Knowledge Graph for deep traversal of a document's extracted knowledge.
    """
    def __init__(self, readonly_repo: ReadOnlyGraphRepository):
        self.repo = readonly_repo

    async def get_document_chunks(self, document_id: str) -> List[ExplorerChunkResponse]:
        query = """
        MATCH (d:Document {id: $doc_id})-[:HAS_CHUNK]->(c:Chunk)
        RETURN c
        ORDER BY c.index ASC
        """
        records = await self.repo.execute_read(query, {"doc_id": document_id})
        chunks = []
        for rec in records:
            c = rec["c"]
            chunks.append(ExplorerChunkResponse(
                id=UUID(c.get("id")),
                index=c.get("index", 0),
                text=c.get("text", ""),
                token_count=c.get("token_usage"),
                embedding_status="COMPLETED"
            ))
        return chunks

    async def get_document_entities(self, document_id: str) -> List[ExplorerEntityResponse]:
        query = """
        MATCH (d:Document {id: $doc_id})-[:HAS_CHUNK]->(c:Chunk)-[:MENTIONS]->(e:Entity)
        RETURN DISTINCT e
        """
        records = await self.repo.execute_read(query, {"doc_id": document_id})
        entities = []
        for rec in records:
            e = rec["e"]
            entities.append(ExplorerEntityResponse(
                id=e.get("id"),
                name=e.get("name", ""),
                category=e.get("type", "UNKNOWN"),
                confidence=e.get("confidence", 1.0)
            ))
        return entities

    async def get_document_relationships(self, document_id: str) -> List[ExplorerRelationshipResponse]:
        query = """
        MATCH (d:Document {id: $doc_id})-[:HAS_CHUNK]->(c:Chunk)-[:MENTIONS]->(sub:Entity)-[r]->(obj:Entity)
        RETURN sub, r, obj
        """
        records = await self.repo.execute_read(query, {"doc_id": document_id})
        rels = []
        for rec in records:
            sub = rec["sub"]
            r = rec["r"]
            obj = rec["obj"]
            # Exclude structural edges
            if r.type in ["HAS_CHUNK", "MENTIONS"]:
                continue
            
            rels.append(ExplorerRelationshipResponse(
                id=str(r.element_id),
                subject_id=sub.get("id"),
                subject_name=sub.get("name", ""),
                predicate=r.type,
                object_id=obj.get("id"),
                object_name=obj.get("name", ""),
                quality_score=r.get("quality_score", 0.0),
                status=r.get("status", "ACTIVE")
            ))
        return rels
