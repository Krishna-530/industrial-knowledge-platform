from uuid import UUID
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.document_content import DocumentContent
from core.enums.processing_status import ProcessingStatus

class DocumentContentRepository:
    """
    Persistence-only repository for DocumentContent.
    No parsing, no validation, no transactions.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document_version_id: UUID) -> DocumentContent:
        content = DocumentContent(
            document_version_id=document_version_id,
            processing_status=ProcessingStatus.PENDING
        )
        self.session.add(content)
        await self.session.flush()
        return content

    async def get_by_version(self, document_version_id: UUID) -> Optional[DocumentContent]:
        result = await self.session.execute(
            select(DocumentContent).where(DocumentContent.document_version_id == document_version_id)
        )
        return result.scalars().first()

    async def update(self, content: DocumentContent, **fields) -> DocumentContent:
        for key, value in fields.items():
            setattr(content, key, value)
        await self.session.flush()
        return content

    async def delete(self, document_version_id: UUID) -> bool:
        content = await self.get_by_version(document_version_id)
        if not content:
            return False
        await self.session.delete(content)
        await self.session.flush()
        return True

    async def exists(self, document_version_id: UUID) -> bool:
        content = await self.get_by_version(document_version_id)
        return content is not None
