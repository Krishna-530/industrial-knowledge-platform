from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models.category import Category
from core.exceptions import DuplicateEntityError

class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        result = await self.session.execute(select(Category).where(Category.id == category_id))
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[Category]:
        result = await self.session.execute(select(Category).where(Category.name == name))
        return result.scalars().first()

    async def create(self, *, name: str, description: Optional[str] = None) -> Category:
        category = Category(name=name, description=description)
        self.session.add(category)
        try:
            await self.session.flush()
            return category
        except IntegrityError:
            raise DuplicateEntityError(message=f"Category {name} already exists")

    async def update(self, category_id: UUID, **fields) -> Optional[Category]:
        category = await self.get_by_id(category_id)
        if not category:
            return None
        
        for key, value in fields.items():
            setattr(category, key, value)
            
        try:
            await self.session.flush()
            return category
        except IntegrityError:
            raise DuplicateEntityError(message="Integrity constraint violated during category update")

    async def delete(self, category_id: UUID) -> bool:
        category = await self.get_by_id(category_id)
        if not category:
            return False
            
        # Due to ON DELETE RESTRICT on Document.category_id, this flush may raise IntegrityError
        # The service layer will handle catching this or we can catch it here.
        # Requirements: "If any Document references a Category: Reject deletion. Raise the existing business exception."
        # We can let the service layer handle the IntegrityError, or wrap it here.
        try:
            await self.session.delete(category)
            await self.session.flush()
            return True
        except IntegrityError:
            # We'll use a generic DuplicateEntityError or similar, wait, maybe ForbiddenError or a custom one
            # The instructions say "Raise the existing business exception."
            from core.exceptions import ForbiddenError
            raise ForbiddenError(message="Cannot delete category because it is referenced by one or more documents.")

    async def list(self, *, limit: int = 50, offset: int = 0) -> List[Category]:
        result = await self.session.execute(select(Category).limit(limit).offset(offset))
        return list(result.scalars().all())
