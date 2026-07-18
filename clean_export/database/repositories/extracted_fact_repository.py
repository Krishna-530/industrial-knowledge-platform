from typing import List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.extracted_fact import ExtractedFact, FactStatus
from database.models.document import Document
from typing import Optional

class ExtractedFactRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_batch(self, facts: List[ExtractedFact]) -> List[ExtractedFact]:
        self.session.add_all(facts)
        await self.session.flush()
        return facts
        
    async def get_by_document(self, document_id: UUID, status: FactStatus = FactStatus.ACTIVE) -> List[ExtractedFact]:
        stmt = select(ExtractedFact).where(
            ExtractedFact.document_id == document_id,
            ExtractedFact.status == status
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_stale_by_document(self, document_id: UUID):
        stmt = update(ExtractedFact).where(
            ExtractedFact.document_id == document_id,
            ExtractedFact.status == FactStatus.ACTIVE
        ).values(status=FactStatus.STALE)
        await self.session.execute(stmt)
        
    async def mark_archived_by_document(self, document_id: UUID):
        stmt = update(ExtractedFact).where(
            ExtractedFact.document_id == document_id,
            ExtractedFact.status == FactStatus.STALE
        ).values(status=FactStatus.ARCHIVED)
        await self.session.execute(stmt)
        
    async def delete_archived_by_document(self, document_id: UUID):
        stmt = delete(ExtractedFact).where(
            ExtractedFact.document_id == document_id,
            ExtractedFact.status == FactStatus.ARCHIVED
        )
        await self.session.execute(stmt)

    async def list_facts_paginated(self, owner_id: UUID, limit: int = 50, cursor_id: Optional[UUID] = None) -> List[ExtractedFact]:
        stmt = (
            select(ExtractedFact)
            .join(Document, ExtractedFact.document_id == Document.id)
            .where(Document.owner_id == owner_id, ExtractedFact.status == FactStatus.ACTIVE)
            .order_by(ExtractedFact.id)
            .limit(limit)
        )
        if cursor_id:
            # We assume UUIDs are sortable, but technically we should order by created_at then id.
            # For simplicity in cursor pagination, we'll filter by id > cursor_id.
            stmt = stmt.where(ExtractedFact.id > cursor_id)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def count_facts(self, owner_id: UUID) -> int:
        from sqlalchemy import func
        stmt = (
            select(func.count(ExtractedFact.id))
            .join(Document, ExtractedFact.document_id == Document.id)
            .where(Document.owner_id == owner_id, ExtractedFact.status == FactStatus.ACTIVE)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def list_facts_by_asset_paginated(self, owner_id: UUID, asset_id: str, limit: int = 50, cursor_id: Optional[UUID] = None) -> List[ExtractedFact]:
        stmt = (
            select(ExtractedFact)
            .join(Document, ExtractedFact.document_id == Document.id)
            .where(
                Document.owner_id == owner_id, 
                ExtractedFact.status == FactStatus.ACTIVE,
                ExtractedFact.asset_id == asset_id
            )
            .order_by(ExtractedFact.id)
            .limit(limit)
        )
        if cursor_id:
            stmt = stmt.where(ExtractedFact.id > cursor_id)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
