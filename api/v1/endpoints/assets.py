from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.dashboard_service import DashboardService
from app.security.context import SecurityContext
from dependencies.auth import get_security_context
from api.v1.schemas.dashboard import (
    AssetSummary, AssetDetailResponse, FactSummary, FindingSummary, CursorPage
)
from api.v1.dependencies.providers import provide_dashboard_service

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("", response_model=CursorPage[AssetSummary])
async def list_assets(
    cursor: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    context: SecurityContext = Depends(get_security_context),
    service: DashboardService = Depends(provide_dashboard_service)
):
    """List assets using cursor pagination."""
    return await service.list_assets(context, cursor, limit)

@router.get("/{asset_id}", response_model=AssetDetailResponse)
async def get_asset(
    asset_id: str,
    context: SecurityContext = Depends(get_security_context),
    service: DashboardService = Depends(provide_dashboard_service)
):
    """Get metadata and overview for a specific asset."""
    return await service.get_asset_details(asset_id, context)

@router.get("/{asset_id}/facts", response_model=CursorPage[FactSummary])
async def list_asset_facts(
    asset_id: str,
    cursor: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    context: SecurityContext = Depends(get_security_context),
    service: DashboardService = Depends(provide_dashboard_service)
):
    """Paginated facts for an asset."""
    return await service.list_asset_facts(asset_id, context, cursor, limit)

@router.get("/{asset_id}/findings", response_model=CursorPage[FindingSummary])
async def list_asset_findings(
    asset_id: str,
    cursor: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    context: SecurityContext = Depends(get_security_context),
    service: DashboardService = Depends(provide_dashboard_service)
):
    """Paginated findings for an asset."""
    return await service.list_asset_findings(asset_id, context, cursor, limit)
