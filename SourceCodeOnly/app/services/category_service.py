from typing import List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from database.repositories.category import CategoryRepository
from api.v1.schemas.category import CategoryRequest
from core.exceptions import EntityNotFoundError

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.category_repo = CategoryRepository(session)

    async def create_category(self, data: CategoryRequest):
        category = await self.category_repo.create(name=data.name, description=data.description)
        await self.session.commit()
        return category

    async def get_category(self, category_id: UUID):
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise EntityNotFoundError(message="Category not found")
        return category

    async def list_categories(self, limit: int = 50, offset: int = 0) -> Tuple[List, int]:
        categories = await self.category_repo.list(limit=limit, offset=offset)
        # Assuming total count is same as list for now, as repo doesn't implement count for categories
        return categories, len(categories)

    async def update_category(self, category_id: UUID, data: CategoryRequest):
        category = await self.get_category(category_id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return category

        updated = await self.category_repo.update(category_id, **update_data)
        await self.session.commit()
        return updated

    async def delete_category(self, category_id: UUID):
        # The repo throws ForbiddenError if it's referenced, per requirements
        deleted = await self.category_repo.delete(category_id)
        if not deleted:
            raise EntityNotFoundError(message="Category not found")
        await self.session.commit()
        return True
