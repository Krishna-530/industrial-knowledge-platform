from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models.user import User
from core.exceptions import EntityNotFoundError, DuplicateEntityError

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, *, name: str, email: str, password_hash: str, role_id: UUID) -> User:
        user = User(name=name, email=email, password_hash=password_hash, role_id=role_id)
        self.session.add(user)
        try:
            await self.session.flush()
            return user
        except IntegrityError:
            raise DuplicateEntityError(message=f"User with email {email} already exists")

    async def update(self, user_id: UUID, **fields) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in fields.items():
            setattr(user, key, value)
            
        try:
            await self.session.flush()
            return user
        except IntegrityError:
            raise DuplicateEntityError(message="Integrity constraint violated during update")

    async def delete(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
            
        await self.session.delete(user)
        await self.session.flush()
        return True

    async def list(self, *, limit: int = 50, offset: int = 0) -> List[User]:
        result = await self.session.execute(select(User).limit(limit).offset(offset))
        return list(result.scalars().all())
