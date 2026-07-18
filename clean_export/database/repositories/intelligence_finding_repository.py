from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from database.models.intelligence_finding import IntelligenceFinding, FindingType
from database.models.extracted_fact import ExtractedFact
from database.models.document import Document

class IntelligenceFindingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def upsert(self, finding: IntelligenceFinding) -> IntelligenceFinding:
        """
        Upsert a finding based on the unique constraint (asset_id, property, type).
        If it exists, update affected_fact_ids.
        """
        stmt = insert(IntelligenceFinding).values(
            type=finding.type,
            asset_id=finding.asset_id,
            property=finding.property,
            affected_fact_ids=finding.affected_fact_ids
        )
        
        # On conflict update affected_fact_ids
        stmt = stmt.on_conflict_do_update(
            index_elements=["asset_id", "property", "type"],
            set_=dict(affected_fact_ids=stmt.excluded.affected_fact_ids)
        ).returning(IntelligenceFinding)
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one()

    async def delete_by_asset_and_property(self, asset_id: str, property_name: str):
        """
        Delete all findings for a given asset and property. Used during re-evaluation.
        """
        stmt = delete(IntelligenceFinding).where(
            IntelligenceFinding.asset_id == asset_id,
            IntelligenceFinding.property == property_name
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_by_asset(self, asset_id: str) -> List[IntelligenceFinding]:
        stmt = select(IntelligenceFinding).where(IntelligenceFinding.asset_id == asset_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    def _tenant_filter(self, owner_id: UUID):
        # Returns a subquery condition ensuring the finding's asset_id belongs to the owner's documents
        from sqlalchemy import exists
        return exists().where(
            (ExtractedFact.asset_id == IntelligenceFinding.asset_id) &
            (ExtractedFact.document_id == Document.id) &
            (Document.owner_id == owner_id)
        )

    async def list_findings_paginated(self, owner_id: UUID, limit: int = 50, cursor_id: Optional[UUID] = None, finding_type: Optional[FindingType] = None) -> List[IntelligenceFinding]:
        stmt = (
            select(IntelligenceFinding)
            .where(self._tenant_filter(owner_id))
            .order_by(IntelligenceFinding.id)
            .limit(limit)
        )
        if finding_type:
            stmt = stmt.where(IntelligenceFinding.type == finding_type)
        if cursor_id:
            stmt = stmt.where(IntelligenceFinding.id > cursor_id)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def count_findings(self, owner_id: UUID, finding_type: Optional[FindingType] = None) -> int:
        from sqlalchemy import func
        stmt = (
            select(func.count(IntelligenceFinding.id))
            .where(self._tenant_filter(owner_id))
        )
        if finding_type:
            stmt = stmt.where(IntelligenceFinding.type == finding_type)
            
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def list_findings_by_asset_paginated(self, owner_id: UUID, asset_id: str, limit: int = 50, cursor_id: Optional[UUID] = None) -> List[IntelligenceFinding]:
        stmt = (
            select(IntelligenceFinding)
            .where(
                self._tenant_filter(owner_id),
                IntelligenceFinding.asset_id == asset_id
            )
            .order_by(IntelligenceFinding.id)
            .limit(limit)
        )
        if cursor_id:
            stmt = stmt.where(IntelligenceFinding.id > cursor_id)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
