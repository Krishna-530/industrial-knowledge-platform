import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database.repositories.intelligence_finding_repository import IntelligenceFindingRepository
from database.models.intelligence_finding import IntelligenceFinding, FindingType

logger = logging.getLogger(__name__)

class KnowledgeIntelligenceService:
    def __init__(self, session: AsyncSession, finding_repo: IntelligenceFindingRepository):
        self.session = session
        self.finding_repo = finding_repo

    async def evaluate_asset_property(self, asset_id: str, property_name: str):
        """
        Evaluates facts for a specific asset and property to detect anomalies.
        Uses SQL aggregation directly for deterministic O(1) LLM cost.
        """
        # First, purge old findings for this specific asset+property
        await self.finding_repo.delete_by_asset_and_property(asset_id, property_name)

        # SQL to find conflicts and corroborations
        # A conflict is multiple distinct values.
        # A corroboration is the same value across multiple documents.
        # A duplicate record is the same value in the same document.
        
        sql = text("""
            WITH property_facts AS (
                SELECT 
                    id, 
                    value, 
                    document_id,
                    chunk_id
                FROM extracted_facts
                WHERE asset_id = :asset_id 
                  AND property = :property_name
                  AND status = 'ACTIVE'
            ),
            value_stats AS (
                SELECT 
                    value,
                    array_agg(id::text) as fact_ids,
                    count(distinct document_id) as doc_count,
                    count(id) as total_occurrences
                FROM property_facts
                GROUP BY value
            )
            SELECT * FROM value_stats
        """)
        
        result = await self.session.execute(sql, {"asset_id": asset_id, "property_name": property_name})
        rows = result.fetchall()
        
        if not rows:
            return
            
        distinct_values = len(rows)
        
        # 1. Conflict Detection
        if distinct_values > 1:
            # We have multiple distinct values for the same property!
            all_fact_ids = []
            for r in rows:
                all_fact_ids.extend(r.fact_ids)
                
            conflict_finding = IntelligenceFinding(
                type=FindingType.CONFLICT,
                asset_id=asset_id,
                property=property_name,
                affected_fact_ids=all_fact_ids
            )
            await self.finding_repo.upsert(conflict_finding)
            
        # 2. Corroboration & Duplicate Detection
        for r in rows:
            # If doc_count > 1, the same value appears in multiple documents (Corroboration)
            if r.doc_count > 1:
                corr_finding = IntelligenceFinding(
                    type=FindingType.CORROBORATION,
                    asset_id=asset_id,
                    property=property_name,
                    affected_fact_ids=r.fact_ids
                )
                await self.finding_repo.upsert(corr_finding)
                
            # If total_occurrences > doc_count, we have multiple of the same value in the same document (Duplicate Record / Bug)
            if r.total_occurrences > r.doc_count:
                dup_finding = IntelligenceFinding(
                    type=FindingType.DUPLICATE_RECORD,
                    asset_id=asset_id,
                    property=property_name,
                    affected_fact_ids=r.fact_ids
                )
                await self.finding_repo.upsert(dup_finding)
                
        logger.info(f"Evaluated intelligence for {asset_id}.{property_name}")
