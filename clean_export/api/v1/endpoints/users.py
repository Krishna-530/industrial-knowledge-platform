from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.user import (
    CreateUserRequest, UpdateUserRequest, UpdatePasswordRequest,
    UpdateRoleRequest, UserResponse, UserListResponse
)
from database.engine import get_db_session
from dependencies.auth import get_current_user, RoleChecker
from api.v1.schemas.auth import User as CurrentUser
from app.services.user_service import UserService

router = APIRouter()

# --- Self Service ---

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    return await service.get_user(UUID(current_user.user_id))

@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UpdateUserRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    return await service.update_me(UUID(current_user.user_id), data)


# --- Admin Only ---

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["Admin"]))])
async def create_user(
    data: CreateUserRequest,
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    return await service.create_user(data)

@router.get("", response_model=UserListResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def list_users(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    users = await service.list_users(limit=limit, offset=offset)
    return UserListResponse(items=users, total=len(users))

@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    return await service.get_user(user_id)

@router.patch("/{user_id}", response_model=UserResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def update_user(
    user_id: UUID,
    data: UpdateUserRequest,
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    return await service.update_user(user_id, data)

@router.patch("/{user_id}/activate", response_model=UserResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    return await service.activate_user(user_id)

@router.patch("/{user_id}/deactivate", response_model=UserResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def deactivate_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    return await service.deactivate_user(user_id, UUID(current_user.user_id))

@router.patch("/{user_id}/role", response_model=UserResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def assign_role(
    user_id: UUID,
    data: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    return await service.assign_role(user_id, data)

@router.patch("/{user_id}/password", response_model=UserResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def reset_password(
    user_id: UUID,
    data: UpdatePasswordRequest,
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    return await service.update_password(user_id, data)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RoleChecker(["Admin"]))])
async def delete_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    service = UserService(db)
    await service.delete_user(user_id, UUID(current_user.user_id))
