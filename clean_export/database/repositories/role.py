from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models.role import Role
from core.exceptions import DuplicateEntityError

class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, role_id: UUID) -> Optional[Role]:
        result = await self.session.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[Role]:
        result = await self.session.execute(select(Role).where(Role.name == name))
        return result.scalars().first()

    async def create(self, *, name: str, description: Optional[str] = None) -> Role:
        role = Role(name=name, description=description)
        self.session.add(role)
        try:
            await self.session.flush()
            return role
        except IntegrityError:
            raise DuplicateEntityError(message=f"Role {name} already exists")

    async def update(self, role_id: UUID, **fields) -> Optional[Role]:
        role = await self.get_by_id(role_id)
        if not role:
            return None
        
        for key, value in fields.items():
            setattr(role, key, value)
            
        try:
            await self.session.flush()
            return role
        except IntegrityError:
            raise DuplicateEntityError(message="Integrity constraint violated during update")

    async def delete(self, role_id: UUID) -> bool:
        role = await self.get_by_id(role_id)
        if not role:
            return False
            
        await self.session.delete(role)
        await self.session.flush()
        return True

    async def list(self, *, limit: int = 50, offset: int = 0) -> List[Role]:
        result = await self.session.execute(select(Role).limit(limit).offset(offset))
        return list(result.scalars().all())
