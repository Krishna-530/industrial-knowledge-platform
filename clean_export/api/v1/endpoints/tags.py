from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.tag import TagRequest, TagResponse
from database.engine import get_db_session
from dependencies.auth import get_current_user, RoleChecker
from app.services.tag_service import TagService

router = APIRouter()

@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["Admin"]))])
async def create_tag(
    data: TagRequest,
    db: AsyncSession = Depends(get_db_session)
):
    service = TagService(db)
    return await service.create_tag(data)

@router.get("", response_model=List[TagResponse], dependencies=[Depends(get_current_user)])
async def list_tags(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
):
    service = TagService(db)
    tags, _ = await service.list_tags(limit=limit, offset=offset)
    return tags

@router.get("/{tag_id}", response_model=TagResponse, dependencies=[Depends(get_current_user)])
async def get_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    service = TagService(db)
    return await service.get_tag(tag_id)

@router.patch("/{tag_id}", response_model=TagResponse, dependencies=[Depends(RoleChecker(["Admin"]))])
async def update_tag(
    tag_id: UUID,
    data: TagRequest,
    db: AsyncSession = Depends(get_db_session)
):
    service = TagService(db)
    return await service.update_tag(tag_id, data)

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RoleChecker(["Admin"]))])
async def delete_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    service = TagService(db)
    await service.delete_tag(tag_id)
