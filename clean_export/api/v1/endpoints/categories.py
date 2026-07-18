from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.category import CategoryRequest, CategoryResponse
from database.engine import get_db_session
from dependencies.auth import get_current_user, RoleChecker
from app.services.category_service import CategoryService

router = APIRouter()

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["Admin"]))])
async def create_category(
    data: CategoryRequest,
    db: AsyncSession = Depends(get_db_session)
):
    service = CategoryService(db)
    return await service.create_category(data)

@router.get("", response_model=List[CategoryResponse], dependencies=[Depends(get_current_user)])
async def list_categories(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
):
    service = CategoryService(db)
    categories, _ = await service.list_categories(limit=limit, offset=offset)
    return categories

@router.get("/{category_id}", response_model=CategoryResponse, dependencies=[Depends(get_current_user)])
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    service = CategoryService(db)
    return await service.get_category(category_id)

@router.patch("/{category_id}", response_model=CategoryResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def update_category(
    category_id: UUID,
    data: CategoryRequest,
    db: AsyncSession = Depends(get_db_session)
):
    service = CategoryService(db)
    return await service.update_category(category_id, data)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RoleChecker(["Admin"]))])
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    service = CategoryService(db)
    await service.delete_category(category_id)
