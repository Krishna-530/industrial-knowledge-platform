import logging
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.extracted_fact_repository import ExtractedFactRepository
from database.models.extracted_fact import ExtractedFact
from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService

logger = logging.getLogger(__name__)

class KnowledgeFactService:
    def __init__(self, session: AsyncSession, fact_repo: ExtractedFactRepository, intelligence_service: KnowledgeIntelligenceService = None):
        self.session = session
        self.fact_repo = fact_repo
        self.intelligence_service = intelligence_service

    async def mark_stale_for_document(self, document_id: UUID):
        """Transition ACTIVE facts to STALE for a document that was updated."""
        await self.fact_repo.mark_stale_by_document(document_id)
        logger.info(f"Marked facts STALE for document {document_id}")

    async def complete_extraction(self, document_id: UUID, new_facts: List[ExtractedFact]):
        """
        Save new ACTIVE facts and transition STALE facts to ARCHIVED.
        This runs after successful extraction.
        """
        # Save new active facts
        await self.fact_repo.create_batch(new_facts)
        
        # Archive the old stale facts
        await self.fact_repo.mark_archived_by_document(document_id)
        logger.info(f"Completed extraction for document {document_id}. Stored {len(new_facts)} facts. Archived STALE facts.")
        
        # Trigger intelligence re-evaluation for all affected asset/property pairs
        if self.intelligence_service:
            evaluated = set()
            for fact in new_facts:
                key = (fact.asset_id, fact.property)
                if key not in evaluated:
                    await self.intelligence_service.evaluate_asset_property(fact.asset_id, fact.property)
                    evaluated.add(key)

    async def purge_archived_facts(self, document_id: UUID):
        """Asynchronously delete ARCHIVED facts."""
        await self.fact_repo.delete_archived_by_document(document_id)
        logger.info(f"Purged ARCHIVED facts for document {document_id}")
