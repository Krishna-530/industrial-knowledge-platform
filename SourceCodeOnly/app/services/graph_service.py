import logging
from typing import List, Dict, Any
from database.repositories.graph_repository import AbstractGraphRepository

logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    """
    Orchestrates business logic for Knowledge Graph construction.
    Acts as a bridge between document processors and the Neo4j Graph Repository.
    """
    def __init__(self, graph_repository: AbstractGraphRepository):
        self.repository = graph_repository

    async def initialize_document_graph(self, document_id: str, title: str, metadata: dict) -> None:
        """
        Creates the root Document node in the graph.
        """
        try:
            await self.repository.create_document_node(document_id, title, metadata)
            logger.info(f"Initialized graph for Document {document_id}")
        except Exception as e:
            logger.error(f"Failed to initialize document graph: {e}")
            raise

    async def process_document_chunks(self, document_id: str, chunks_data: List[Dict[str, Any]]) -> None:
        """
        Processes a list of chunks, creating Chunk nodes and associating them with the Document node.
        chunks_data expects format: [{'chunk_id': '...', 'index': 0}, ...]
        """
        for chunk in chunks_data:
            try:
                await self.repository.create_chunk_node(
                    chunk_id=chunk["chunk_id"], 
                    document_id=document_id, 
                    index=chunk["index"]
                )
            except Exception as e:
                logger.error(f"Failed to create graph chunk {chunk['chunk_id']}: {e}")

    async def ingest_entities(self, chunk_id: str, entities: List[Dict[str, Any]]) -> None:
        """
        Ingests extracted entities and links them to the specified chunk.
        entities expects format: [{'id': '...', 'label': '...', 'name': '...'}, ...]
        """
        for entity in entities:
            try:
                await self.repository.create_entity_node(
                    entity_id=entity["id"], 
                    label=entity["label"], 
                    name=entity["name"]
                )
                await self.repository.link_chunk_to_entity(
                    chunk_id=chunk_id, 
                    entity_id=entity["id"]
                )
            except Exception as e:
                logger.error(f"Failed to ingest entity {entity.get('id')} for chunk {chunk_id}: {e}")

    async def sync_edges(self, edges_data: List[Dict[str, Any]]) -> None:
        """
        Syncs an array of edge outbox events to the Graph Repository.
        """
        try:
            await self.repository.sync_edges(edges_data)
        except Exception as e:
            logger.error(f"Failed to sync edges: {e}")
            raise
