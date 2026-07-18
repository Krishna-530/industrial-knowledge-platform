from typing import List, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from database.repositories.role import RoleRepository
from core.exceptions import EntityNotFoundError

logger = logging.getLogger(__name__)

class RoleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.role_repo = RoleRepository(session)

    async def get_role(self, role_id: UUID):
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise EntityNotFoundError(message="Role not found")
        return role

    async def list_roles(self, limit: int = 50, offset: int = 0) -> List[Any]:
        roles = await self.role_repo.list(limit=limit, offset=offset)
        return roles
