from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.role import RoleResponse, RoleListResponse
from database.engine import get_db_session
from dependencies.auth import get_current_user, RoleChecker
from app.services.role_service import RoleService

router = APIRouter()

@router.get("", response_model=RoleListResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def list_roles(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
):
    service = RoleService(db)
    roles = await service.list_roles(limit=limit, offset=offset)
    return RoleListResponse(items=roles, total=len(roles))

@router.get("/{role_id}", response_model=RoleResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    service = RoleService(db)
    return await service.get_role(role_id)
