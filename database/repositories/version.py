from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.document_version import DocumentVersion

class VersionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, document_id: UUID, version_number: int, uploaded_by: UUID, storage_identifier: Optional[str] = None, checksum: Optional[str] = None) -> DocumentVersion:
        version = DocumentVersion(
            document_id=document_id,
            version_number=version_number,
            uploaded_by=uploaded_by,
            storage_identifier=storage_identifier,
            checksum=checksum
        )
        self.session.add(version)
        await self.session.flush()
        return version

    async def get_latest_version(self, document_id: UUID) -> Optional[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def list_by_document(self, document_id: UUID) -> List[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
        )
        return list(result.scalars().all())
