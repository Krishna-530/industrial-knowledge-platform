from uuid import UUID
from typing import Optional, List, Tuple, Any, Dict
from app.services.dashboard_service import DashboardService
from app.services.user_service import UserService
from app.services.document_service import DocumentService
from app.services.job_service import JobService
from database.repositories.version import VersionRepository
from app.security.context import SecurityContext
from core.exceptions import EntityNotFoundError

class AdminService:
    """
    Orchestration service for the Administration module.
    Delegates to feature-specific services.
    """
    def __init__(
        self,
        dashboard_service: DashboardService,
        user_service: UserService,
        document_service: DocumentService,
        job_service: JobService,
        version_repo: VersionRepository,
        infra_health
    ):
        self.dashboard_service = dashboard_service
        self.user_service = user_service
        self.document_service = document_service
        self.job_service = job_service
        self.version_repo = version_repo
        self.infra_health = infra_health

    async def get_dashboard_overview(self, context: SecurityContext):
        from api.v1.schemas.dashboard import AdminDashboardOverviewResponse, AdminDashboardStats
        from core.enums.job_status import JobStatus
        overview = await self.dashboard_service.get_overview(context)

        # Extend with total users
        total_users = await self.user_service.user_repo.count_all()
        admin_stats = AdminDashboardStats(**overview.stats.model_dump(), total_users=total_users)

        # Retrieve fields that the base dashboard doesn't expose
        job_repo = self.dashboard_service.job_repo
        entity_repo = self.dashboard_service.entity_repo
        relationship_repo = self.dashboard_service.relationship_repo
        chunk_repo = self.dashboard_service.chunk_repo

        queue_metrics = overview.workers
        processing_jobs = queue_metrics.processing

        total_chunks = await chunk_repo.count_all()
        total_entities = await entity_repo.count_all()
        total_relationships = await relationship_repo.count_all()

        # active_conflicts: use finding_repo via analytics service if available, else 0
        try:
            from database.models.intelligence_finding import FindingType
            active_conflicts = await self.dashboard_service.analytics.finding_repo.count_findings(
                context.user_id, FindingType.CONFLICT
            )
        except Exception:
            active_conflicts = 0

        return AdminDashboardOverviewResponse(
            stats=admin_stats,
            graph=overview.graph,
            workers=overview.workers,
            retrieval=overview.retrieval,
            recent_documents=overview.recent_documents,
            processing_queue=overview.processing_queue,
            active_conflicts=active_conflicts,
            processing_jobs=processing_jobs,
            total_chunks=total_chunks,
            total_entities=total_entities,
            total_relationships=total_relationships,
        )

    async def list_users(self, limit: int = 50, offset: int = 0, search: Optional[str] = None, is_active: Optional[bool] = None) -> Tuple[List[Any], int]:
        return await self.user_service.list_users(limit=limit, offset=offset, search=search, is_active=is_active)

    async def list_documents(self, limit: int = 50, offset: int = 0, title_search: Optional[str] = None) -> Tuple[List[Any], int]:
        return await self.document_service.list_documents(limit=limit, offset=offset, title_search=title_search)

    async def list_jobs(self, limit: int = 50, offset: int = 0, status: Optional[str] = None, job_type: Optional[str] = None, search: Optional[str] = None) -> Tuple[List[Any], int]:
        return await self.job_service.list_jobs(limit=limit, offset=offset, status=status, job_type=job_type, search=search)

    async def get_job_details(self, job_id: UUID) -> Dict[str, Any]:
        return await self.job_service.get_job_details(job_id)

    async def retry_job(self, job_id: UUID, context: SecurityContext) -> Any:
        return await self.job_service.retry_job(job_id, context.user_id)

    async def get_system_health(self) -> Dict[str, Any]:
        return await self.infra_health.get_system_health()

    async def reprocess_document(self, document_id: UUID, context: SecurityContext):
        import logging
        logger = logging.getLogger(__name__)
        logger.info({
            "event": "audit_log", 
            "action": "reprocess_document", 
            "document_id": str(document_id), 
            "admin_user_id": str(context.user_id)
        })

        doc = await self.document_service.get_document(document_id)
        latest_version = await self.version_repo.get_latest_version(document_id)
        if not latest_version:
            raise EntityNotFoundError(message="Document has no versions to reprocess")
            
        await self.job_service.enqueue("PROCESS_DOCUMENT", {
            "document_id": str(document_id),
            "version_id": str(latest_version.id)
        })
        
        return doc
