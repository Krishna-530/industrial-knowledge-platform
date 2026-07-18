from typing import List, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from database.repositories.user import UserRepository
from database.repositories.role import RoleRepository
from core.exceptions import EntityNotFoundError, ForbiddenError
from core.security import get_password_hash
from api.v1.schemas.user import CreateUserRequest, UpdateUserRequest, UpdatePasswordRequest, UpdateRoleRequest

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)

    async def _check_role_exists(self, role_id: UUID) -> None:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise EntityNotFoundError(message="Role not found")

    async def create_user(self, data: CreateUserRequest) -> Any: # Returns User model
        await self._check_role_exists(data.role_id)
        
        # Checking email uniqueness happens in repo / DB constraint, but we can rely on repository DuplicateEntityError
        hashed_pwd = get_password_hash(data.password)
        
        user = await self.user_repo.create(
            name=data.name,
            email=data.email,
            password_hash=hashed_pwd,
            role_id=data.role_id
        )
        await self.session.commit()
        logger.info(f"Created new user with email {user.email}")
        return user

    async def get_user(self, user_id: UUID):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(message="User not found")
        return user

    async def list_users(self, limit: int = 50, offset: int = 0) -> List[Any]:
        users = await self.user_repo.list(limit=limit, offset=offset)
        # Note: repository doesn't have a count method currently.
        # We can just return the list and len for total for this phase, assuming limit is applied on return or we fetch all
        return users

    async def update_user(self, user_id: UUID, data: UpdateUserRequest):
        user = await self.get_user(user_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if not update_data:
            return user

        updated_user = await self.user_repo.update(user_id, **update_data)
        await self.session.commit()
        return updated_user

    async def activate_user(self, user_id: UUID):
        user = await self.get_user(user_id)
        if not user.is_active:
            await self.user_repo.update(user_id, is_active=True)
            await self.session.commit()
        return await self.get_user(user_id)

    async def deactivate_user(self, user_id: UUID, current_user_id: UUID):
        if user_id == current_user_id:
            raise ForbiddenError(message="Cannot deactivate yourself")
            
        user = await self.get_user(user_id)
        if user.is_active:
            await self.user_repo.update(user_id, is_active=False)
            await self.session.commit()
        return await self.get_user(user_id)

    async def delete_user(self, user_id: UUID, current_user_id: UUID):
        if user_id == current_user_id:
            raise ForbiddenError(message="Cannot delete yourself")
            
        await self.get_user(user_id)
        await self.user_repo.delete(user_id)
        await self.session.commit()
        return True

    async def update_password(self, user_id: UUID, data: UpdatePasswordRequest):
        await self.get_user(user_id)
        hashed_pwd = get_password_hash(data.password)
        await self.user_repo.update(user_id, password_hash=hashed_pwd)
        await self.session.commit()
        return await self.get_user(user_id)

    async def assign_role(self, user_id: UUID, data: UpdateRoleRequest):
        await self._check_role_exists(data.role_id)
        await self.get_user(user_id)
        await self.user_repo.update(user_id, role_id=data.role_id)
        await self.session.commit()
        return await self.get_user(user_id)

    async def update_me(self, user_id: UUID, data: UpdateUserRequest):
        # same as update_user but for self
        return await self.update_user(user_id, data)
