from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models.role import Permission
from core.exceptions import DuplicateEntityError

class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, permission_id: UUID) -> Optional[Permission]:
        result = await self.session.execute(select(Permission).where(Permission.id == permission_id))
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[Permission]:
        result = await self.session.execute(select(Permission).where(Permission.name == name))
        return result.scalars().first()

    async def create(self, *, name: str, description: Optional[str] = None) -> Permission:
        permission = Permission(name=name, description=description)
        self.session.add(permission)
        try:
            await self.session.flush()
            return permission
        except IntegrityError:
            raise DuplicateEntityError(message=f"Permission {name} already exists")

    async def update(self, permission_id: UUID, **fields) -> Optional[Permission]:
        permission = await self.get_by_id(permission_id)
        if not permission:
            return None
        
        for key, value in fields.items():
            setattr(permission, key, value)
            
        try:
            await self.session.flush()
            return permission
        except IntegrityError:
            raise DuplicateEntityError(message="Integrity constraint violated during update")

    async def delete(self, permission_id: UUID) -> bool:
        permission = await self.get_by_id(permission_id)
        if not permission:
            return False
            
        await self.session.delete(permission)
        await self.session.flush()
        return True

    async def list(self, *, limit: int = 50, offset: int = 0) -> List[Permission]:
        result = await self.session.execute(select(Permission).limit(limit).offset(offset))
        return list(result.scalars().all())
