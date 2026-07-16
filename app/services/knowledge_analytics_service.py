import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.extracted_fact_repository import ExtractedFactRepository
from database.repositories.intelligence_finding_repository import IntelligenceFindingRepository
from database.models.intelligence_finding import FindingType
from api.v1.schemas.analytics import (
    AnalyticsSummary, 
    FindingSummary, 
    ExtractedFactSummary, 
    AssetAnalytics, 
    PaginatedResponse
)

logger = logging.getLogger(__name__)

class KnowledgeAnalyticsService:
    def __init__(self, session: AsyncSession, fact_repo: ExtractedFactRepository, finding_repo: IntelligenceFindingRepository):
        self.session = session
        self.fact_repo = fact_repo
        self.finding_repo = finding_repo

    async def get_summary(self, owner_id: UUID) -> AnalyticsSummary:
        total_facts = await self.fact_repo.count_facts(owner_id)
        total_conflicts = await self.finding_repo.count_findings(owner_id, FindingType.CONFLICT)
        total_corroborations = await self.finding_repo.count_findings(owner_id, FindingType.CORROBORATION)
        total_duplicates = await self.finding_repo.count_findings(owner_id, FindingType.DUPLICATE_RECORD)

        return AnalyticsSummary(
            total_active_facts=total_facts,
            total_conflicts=total_conflicts,
            total_corroborations=total_corroborations,
            total_duplicate_records=total_duplicates
        )

    async def list_findings(self, owner_id: UUID, limit: int = 50, cursor_id: Optional[UUID] = None, finding_type: Optional[FindingType] = None) -> PaginatedResponse[FindingSummary]:
        # Fetch limit + 1 to check if there is more data
        entities = await self.finding_repo.list_findings_paginated(owner_id, limit=limit + 1, cursor_id=cursor_id, finding_type=finding_type)
        
        has_more = len(entities) > limit
        items = entities[:limit]
        next_cursor = str(items[-1].id) if items else None
        
        summaries = [
            FindingSummary(
                id=item.id,
                type=item.type,
                asset_id=item.asset_id,
                property=item.property,
                affected_fact_ids=item.affected_fact_ids
            )
            for item in items
        ]
        
        return PaginatedResponse(items=summaries, next_cursor=next_cursor, has_more=has_more)

    async def get_asset_analytics(self, owner_id: UUID, asset_id: str, limit: int = 50, facts_cursor: Optional[UUID] = None, findings_cursor: Optional[UUID] = None) -> AssetAnalytics:
        # Get Paginated Facts
        fact_entities = await self.fact_repo.list_facts_by_asset_paginated(owner_id, asset_id, limit=limit + 1, cursor_id=facts_cursor)
        facts_has_more = len(fact_entities) > limit
        fact_items = fact_entities[:limit]
        facts_next_cursor = str(fact_items[-1].id) if fact_items else None
        
        fact_summaries = [
            ExtractedFactSummary(
                id=f.id,
                asset_id=f.asset_id,
                property=f.property,
                value=f.value,
                document_id=f.document_id
            )
            for f in fact_items
        ]
        
        facts_page = PaginatedResponse(items=fact_summaries, next_cursor=facts_next_cursor, has_more=facts_has_more)
        
        # Get Paginated Findings
        finding_entities = await self.finding_repo.list_findings_by_asset_paginated(owner_id, asset_id, limit=limit + 1, cursor_id=findings_cursor)
        findings_has_more = len(finding_entities) > limit
        finding_items = finding_entities[:limit]
        findings_next_cursor = str(finding_items[-1].id) if finding_items else None
        
        finding_summaries = [
            FindingSummary(
                id=item.id,
                type=item.type,
                asset_id=item.asset_id,
                property=item.property,
                affected_fact_ids=item.affected_fact_ids
            )
            for item in finding_items
        ]
        
        findings_page = PaginatedResponse(items=finding_summaries, next_cursor=findings_next_cursor, has_more=findings_has_more)
        
        return AssetAnalytics(
            asset_id=asset_id,
            facts=facts_page,
            findings=findings_page
        )
