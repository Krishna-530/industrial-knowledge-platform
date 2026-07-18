from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models.tag import Tag
from core.exceptions import DuplicateEntityError

class TagRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, tag_id: UUID) -> Optional[Tag]:
        result = await self.session.execute(select(Tag).where(Tag.id == tag_id))
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[Tag]:
        result = await self.session.execute(select(Tag).where(Tag.name == name))
        return result.scalars().first()

    async def create(self, *, name: str) -> Tag:
        tag = Tag(name=name)
        self.session.add(tag)
        try:
            await self.session.flush()
            return tag
        except IntegrityError:
            raise DuplicateEntityError(message=f"Tag {name} already exists")

    async def update(self, tag_id: UUID, **fields) -> Optional[Tag]:
        tag = await self.get_by_id(tag_id)
        if not tag:
            return None
        
        for key, value in fields.items():
            setattr(tag, key, value)
            
        try:
            await self.session.flush()
            return tag
        except IntegrityError:
            raise DuplicateEntityError(message="Integrity constraint violated during tag update")

    async def delete(self, tag_id: UUID) -> bool:
        tag = await self.get_by_id(tag_id)
        if not tag:
            return False
            
        await self.session.delete(tag)
        await self.session.flush()
        return True

    async def list(self, *, limit: int = 50, offset: int = 0) -> List[Tag]:
        result = await self.session.execute(select(Tag).limit(limit).offset(offset))
        return list(result.scalars().all())
