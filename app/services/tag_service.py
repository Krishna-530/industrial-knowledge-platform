from typing import List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from database.repositories.tag import TagRepository
from api.v1.schemas.tag import TagRequest
from core.exceptions import EntityNotFoundError

logger = logging.getLogger(__name__)

class TagService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tag_repo = TagRepository(session)

    async def create_tag(self, data: TagRequest):
        tag = await self.tag_repo.create(name=data.name)
        await self.session.commit()
        return tag

    async def get_tag(self, tag_id: UUID):
        tag = await self.tag_repo.get_by_id(tag_id)
        if not tag:
            raise EntityNotFoundError(message="Tag not found")
        return tag

    async def list_tags(self, limit: int = 50, offset: int = 0) -> Tuple[List, int]:
        tags = await self.tag_repo.list(limit=limit, offset=offset)
        return tags, len(tags)

    async def update_tag(self, tag_id: UUID, data: TagRequest):
        tag = await self.get_tag(tag_id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return tag

        updated = await self.tag_repo.update(tag_id, **update_data)
        await self.session.commit()
        return updated

    async def delete_tag(self, tag_id: UUID):
        # Database CASCADE handles removing DocumentTag associations
        deleted = await self.tag_repo.delete(tag_id)
        if not deleted:
            raise EntityNotFoundError(message="Tag not found")
        await self.session.commit()
        return True
