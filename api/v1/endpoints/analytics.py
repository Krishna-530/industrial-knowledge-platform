from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from uuid import UUID
from api.v1.schemas.analytics import AnalyticsSummary, PaginatedResponse, FindingSummary, AssetAnalytics
from api.v1.dependencies.analytics import provide_analytics_service
from app.services.knowledge_analytics_service import KnowledgeAnalyticsService
from database.models.intelligence_finding import FindingType
# We assume there is a standard get_current_user dependency that provides the user info
# For this implementation, we will mock it if it doesn't exist, but typically it returns a User object
from dependencies.auth import get_current_user, RoleChecker
from database.models.user import User

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    analytics_service: KnowledgeAnalyticsService = Depends(provide_analytics_service)
):
    """
    Get a high-level summary of all knowledge analytics for the user's workspace.
    """
    return await analytics_service.get_summary(owner_id=current_user.id)

@router.get("/findings", response_model=PaginatedResponse[FindingSummary])
async def list_findings(
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[UUID] = Query(None),
    type: Optional[FindingType] = Query(None),
    current_user: User = Depends(get_current_user),
    analytics_service: KnowledgeAnalyticsService = Depends(provide_analytics_service)
):
    """
    Get a paginated list of intelligence findings, optionally filtered by type.
    """
    return await analytics_service.list_findings(
        owner_id=current_user.id,
        limit=limit,
        cursor_id=cursor,
        finding_type=type
    )

@router.get("/assets/{asset_id}", response_model=AssetAnalytics)
async def get_asset_analytics(
    asset_id: str = Path(...),
    limit: int = Query(50, ge=1, le=100),
    facts_cursor: Optional[UUID] = Query(None),
    findings_cursor: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    analytics_service: KnowledgeAnalyticsService = Depends(provide_analytics_service)
):
    """
    Get a paginated overview of facts and findings for a specific asset.
    """
    return await analytics_service.get_asset_analytics(
        owner_id=current_user.id,
        asset_id=asset_id,
        limit=limit,
        facts_cursor=facts_cursor,
        findings_cursor=findings_cursor
    )

from app.services.enterprise_analytics_service import EnterpriseAnalyticsService
from api.v1.schemas.enterprise_analytics import EnterpriseAnalyticsResponse
from datetime import datetime
from database.engine import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

async def provide_enterprise_analytics_service(session: AsyncSession = Depends(get_db_session)) -> EnterpriseAnalyticsService:
    return EnterpriseAnalyticsService(session)

@router.get("/enterprise", response_model=EnterpriseAnalyticsResponse,
            dependencies=[Depends(RoleChecker(["Admin", "Manager"]))])
async def get_enterprise_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    service: EnterpriseAnalyticsService = Depends(provide_enterprise_analytics_service)
):
    """
    Get comprehensive enterprise analytics for the platform.
    Requires Manager or Admin role.
    """
    return await service.get_enterprise_analytics(start_date, end_date)
