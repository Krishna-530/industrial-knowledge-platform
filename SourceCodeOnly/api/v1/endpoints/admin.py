from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.security.context import SecurityContext
from dependencies.auth import get_security_context, RoleChecker
from api.v1.schemas.dashboard import AdminDashboardOverviewResponse
from api.v1.schemas.user import UserListResponse
from api.v1.schemas.document import DocumentListResponse, DocumentResponse
from app.services.admin_service import AdminService
from api.v1.dependencies.services import provide_admin_service

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(RoleChecker(["Admin"]))])

@router.get("/dashboard", response_model=AdminDashboardOverviewResponse)
async def get_admin_dashboard(
    context: SecurityContext = Depends(get_security_context),
    service: AdminService = Depends(provide_admin_service)
):
    return await service.get_dashboard_overview(context)

@router.get("/users", response_model=UserListResponse)
async def list_admin_users(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: AdminService = Depends(provide_admin_service)
):
    users, total = await service.list_users(limit=limit, offset=offset, search=search, is_active=is_active)
    return UserListResponse(items=users, total=total)

@router.get("/documents", response_model=DocumentListResponse)
async def list_admin_documents(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    title_search: Optional[str] = Query(None),
    service: AdminService = Depends(provide_admin_service)
):
    documents, total = await service.list_documents(limit=limit, offset=offset, title_search=title_search)
    return DocumentListResponse(items=documents, total=total)

@router.post("/documents/{document_id}/reprocess", response_model=DocumentResponse)
async def reprocess_admin_document(
    document_id: UUID,
    context: SecurityContext = Depends(get_security_context),
    service: AdminService = Depends(provide_admin_service)
):
    return await service.reprocess_document(document_id, context)

from api.v1.schemas.job import JobListResponse, JobDetailResponse, SystemHealthResponse, JobResponse

@router.get("/jobs", response_model=JobListResponse)
async def list_admin_jobs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    service: AdminService = Depends(provide_admin_service)
):
    jobs, total = await service.list_jobs(limit=limit, offset=offset, status=status, job_type=job_type, search=search)
    return JobListResponse(items=jobs, total=total)

@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
async def get_admin_job(
    job_id: UUID,
    service: AdminService = Depends(provide_admin_service)
):
    return await service.get_job_details(job_id)

@router.post("/jobs/{job_id}/retry", response_model=JobResponse)
async def retry_admin_job(
    job_id: UUID,
    context: SecurityContext = Depends(get_security_context),
    service: AdminService = Depends(provide_admin_service)
):
    return await service.retry_job(job_id, context)

@router.get("/health", response_model=SystemHealthResponse)
async def get_admin_system_health(
    service: AdminService = Depends(provide_admin_service)
):
    return await service.get_system_health()
