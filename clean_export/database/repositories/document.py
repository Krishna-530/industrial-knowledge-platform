from uuid import UUID
from typing import List, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from database.models.document import Document
from core.enums import DocumentStatus
from core.exceptions import DuplicateEntityError

class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        result = await self.session.execute(select(Document).where(Document.id == document_id))
        return result.scalars().first()

    async def get_by_id_for_update(self, document_id: UUID) -> Optional[Document]:
        result = await self.session.execute(
            select(Document).where(Document.id == document_id).with_for_update()
        )
        return result.scalars().first()

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count(Document.id)))
        return result.scalar() or 0

    async def create(self, *, title: str, owner_id: UUID, category_id: UUID, description: Optional[str] = None, tags: List[Any] = None) -> Document:
        doc = Document(
            title=title,
            description=description,
            owner_id=owner_id,
            category_id=category_id,
            current_version=1,
            status=DocumentStatus.DRAFT,
            tags=tags or []
        )
        self.session.add(doc)
        try:
            await self.session.flush()
            return doc
        except IntegrityError:
            raise DuplicateEntityError(message="Database integrity error during document creation")

    async def update(self, document_id: UUID, **fields) -> Optional[Document]:
        doc = await self.get_by_id(document_id)
        if not doc:
            return None
        
        tags = fields.pop("tags", None)
        if tags is not None:
            doc.tags = tags
            
        for key, value in fields.items():
            setattr(doc, key, value)
            
        try:
            await self.session.flush()
            return doc
        except IntegrityError:
            raise DuplicateEntityError(message="Database integrity error during document update")

    async def delete(self, document_id: UUID) -> bool:
        doc = await self.get_by_id(document_id)
        if not doc:
            return False
            
        await self.session.delete(doc)
        await self.session.flush()
        return True

    async def list(
        self, 
        *, 
        limit: int = 50, 
        offset: int = 0, 
        owner_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        status: Optional[DocumentStatus] = None,
        title_search: Optional[str] = None
    ) -> Tuple[List[Document], int]:
        
        query = select(Document)
        count_query = select(func.count(Document.id))
        
        if owner_id:
            query = query.where(Document.owner_id == owner_id)
            count_query = count_query.where(Document.owner_id == owner_id)
        if category_id:
            query = query.where(Document.category_id == category_id)
            count_query = count_query.where(Document.category_id == category_id)
        if status:
            query = query.where(Document.status == status)
            count_query = count_query.where(Document.status == status)
        if title_search:
            query = query.where(Document.title.ilike(f"%{title_search}%"))
            count_query = count_query.where(Document.title.ilike(f"%{title_search}%"))
            
        # Default sorting by created_at DESC
        query = query.order_by(Document.created_at.desc())
        
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)
        
        return list(result.scalars().all()), count_result.scalar()

    async def create_version(self, document_id: UUID, new_version: int) -> Document:
        doc = await self.get_by_id(document_id)
        if doc:
            doc.current_version = new_version
            await self.session.flush()
        return doc
