from fastapi import APIRouter, Depends
from app.services.dashboard_service import DashboardService
from app.security.context import SecurityContext
from dependencies.auth import get_security_context
from api.v1.schemas.dashboard import DashboardOverviewResponse
from api.v1.dependencies.providers import provide_dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    context: SecurityContext = Depends(get_security_context),
    service: DashboardService = Depends(provide_dashboard_service)
):
    """
    Projection API for dashboard overview metrics.
    Read-only.
    """
    return await service.get_overview(context)
