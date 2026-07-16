import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from neo4j import AsyncDriver

logger = logging.getLogger(__name__)

class AbstractGraphRepository(ABC):
    """
    Abstract contract for all Knowledge Graph interactions.
    Ensures that domain services do not depend directly on neo4j driver APIs.
    """
    
    @abstractmethod
    async def create_document_node(self, document_id: str, title: str, metadata: dict) -> None:
        pass
        
    @abstractmethod
    async def create_chunk_node(self, chunk_id: str, document_id: str, index: int) -> None:
        pass

    @abstractmethod
    async def create_entity_node(self, entity_id: str, label: str, name: str) -> None:
        pass

    @abstractmethod
    async def link_chunk_to_entity(self, chunk_id: str, entity_id: str, relation_type: str = "MENTIONS") -> None:
        pass

    @abstractmethod
    async def sync_edges(self, edges_data: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass


class Neo4jGraphRepository(AbstractGraphRepository):
    """
    Concrete implementation of the AbstractGraphRepository for Neo4j.
    """
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def create_document_node(self, document_id: str, title: str, metadata: dict) -> None:
        query = """
        MERGE (d:Document {id: $document_id})
        SET d.title = $title, d += $metadata
        """
        async with self.driver.session() as session:
            await session.run(query, document_id=str(document_id), title=title, metadata=metadata)

    async def create_chunk_node(self, chunk_id: str, document_id: str, index: int) -> None:
        query = """
        MATCH (d:Document {id: $document_id})
        MERGE (c:Chunk {id: $chunk_id})
        SET c.index = $index
        MERGE (d)-[:HAS_CHUNK]->(c)
        """
        async with self.driver.session() as session:
            await session.run(query, chunk_id=str(chunk_id), document_id=str(document_id), index=index)

    async def create_entity_node(self, entity_id: str, label: str, name: str) -> None:
        # Dynamic labels require apoc or f-strings. We'll use a generic Entity node with a type property for safety
        query = """
        MERGE (e:Entity {id: $entity_id})
        SET e.type = $label, e.name = $name
        """
        async with self.driver.session() as session:
            await session.run(query, entity_id=str(entity_id), label=label, name=name)

    async def link_chunk_to_entity(self, chunk_id: str, entity_id: str, relation_type: str = "MENTIONS") -> None:
        # For dynamic relationships, we use APOC if available, or fallback. 
        # Since relation_type is usually static (MENTIONS), we can hardcode for now or parameterize carefully.
        query = f"""
        MATCH (c:Chunk {{id: $chunk_id}})
        MATCH (e:Entity {{id: $entity_id}})
        MERGE (c)-[:{relation_type}]->(e)
        """
        async with self.driver.session() as session:
            await session.run(query, chunk_id=str(chunk_id), entity_id=str(entity_id))

    async def sync_edges(self, edges_data: List[Dict[str, Any]]) -> None:
        """
        Batch syncs edges to Neo4j. Incorporates Node Fallback MERGE 
        to guarantee topological idempotency.
        edges_data format: [{'subject_id': '...', 'predicate': '...', 'object_id': '...', 'quality_score': 0.9, 'status': 'ACTIVE'}]
        """
        # In a real environment with thousands of relationships, we might use APOC and UNWIND.
        # For now, we will execute a dynamic query per edge or group by predicate for safety.
        async with self.driver.session() as session:
            for edge in edges_data:
                predicate = edge['predicate']
                query = f"""
                MERGE (s:Entity {{id: $subject_id}})
                MERGE (o:Entity {{id: $object_id}})
                MERGE (s)-[r:{predicate}]->(o)
                SET r.quality_score = $quality_score, r.status = $status
                """
                await session.run(
                    query, 
                    subject_id=str(edge['subject_id']), 
                    object_id=str(edge['object_id']),
                    quality_score=edge['quality_score'],
                    status=edge['status']
                )

    async def health_check(self) -> bool:
        try:
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 AS num")
                record = await result.single()
                return record["num"] == 1 if record else False
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False
