from typing import Optional
import asyncio
from app.security.context import SecurityContext
from api.v1.schemas.dashboard import (
    DashboardOverviewResponse, DashboardStats, KnowledgeGraphStats,
    WorkerQueueStats, RetrievalStats, RecentDocument, ProcessingQueueItem,
    AssetSummary, AssetDetailResponse, FactSummary, FindingSummary, CursorPage
)
from app.services.knowledge_analytics_service import KnowledgeAnalyticsService
from app.services.document_service import DocumentService
from app.services.graph_query_service import GraphQueryService
from database.repositories.document import DocumentRepository
from database.repositories.document_chunk_repository import DocumentChunkRepository
from database.repositories.entity_repository import EntityRepository
from database.repositories.relationship_repository import RelationshipRepository
from database.repositories.job_repository import JobRepository
from core.enums.job_status import JobStatus

class DashboardService:
    """
    Presentation layer service for aggregating read-models.
    Strictly forbidden from querying repositories directly via SQL/Cypher.
    Orchestrates repository read-methods and existing services.
    """
    def __init__(
        self, 
        analytics_service: KnowledgeAnalyticsService, 
        document_service: DocumentService,
        graph_service: GraphQueryService,
        document_repo: DocumentRepository,
        chunk_repo: DocumentChunkRepository,
        entity_repo: EntityRepository,
        relationship_repo: RelationshipRepository,
        job_repo: JobRepository
    ):
        self.analytics = analytics_service
        self.documents = document_service
        self.graph = graph_service
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.entity_repo = entity_repo
        self.relationship_repo = relationship_repo
        self.job_repo = job_repo

    async def get_overview(self, context: SecurityContext) -> DashboardOverviewResponse:
        # Run independent queries in parallel using asyncio.gather
        results = await asyncio.gather(
            self.document_repo.count_all(),
            self.chunk_repo.count_all(),
            self.entity_repo.count_all(),
            self.relationship_repo.count_all(),
            self.graph.get_statistics(),
            self.job_repo.get_queue_metrics(),
            self.document_repo.list(limit=5),
            self.job_repo.get_recent_jobs(limit=10)
        )
        
        doc_count, chunk_count, entity_count, rel_count, graph_stats, queue_metrics, docs_tuple, recent_jobs = results
        recent_docs, _ = docs_tuple
        
        # Build Stats
        stats = DashboardStats(
            total_documents=doc_count,
            total_assets=0
        )
        
        # Build Knowledge Graph
        # Note: sync_lag is unavailable because it's not tracked
        kg_stats = KnowledgeGraphStats(
            total_nodes=graph_stats.get("total_nodes", 0),
            total_edges=graph_stats.get("total_edges", 0),
            sync_lag=None,
            status="unavailable" # explicitly unavailable because no real lag metric exists
        )
        
        # Build Worker Queue
        worker_stats = WorkerQueueStats(
            queued=queue_metrics.get(JobStatus.QUEUED.value, 0),
            processing=queue_metrics.get(JobStatus.PROCESSING.value, 0),
            completed=queue_metrics.get(JobStatus.COMPLETED.value, 0),
            failed=queue_metrics.get(JobStatus.FAILED.value, 0),
            total=queue_metrics.get("TOTAL", 0)
        )
        
        # Build Retrieval Stats (Unavailable because telemetry is only logged, not persisted)
        retrieval_stats = RetrievalStats(
            total_searches=None,
            average_latency=None,
            status="unavailable"
        )
        
        # Map recent items
        mapped_docs = [
            RecentDocument(id=d.id, title=d.title, status=d.status.value, uploaded_at=d.created_at)
            for d in recent_docs
        ]
        
        mapped_jobs = [
            ProcessingQueueItem(job_id=j.id, job_type=j.job_type, status=j.status.value, started_at=j.started_at)
            for j in recent_jobs
        ]
        
        return DashboardOverviewResponse(
            stats=stats,
            graph=kg_stats,
            workers=worker_stats,
            retrieval=retrieval_stats,
            recent_documents=mapped_docs,
            processing_queue=mapped_jobs
        )

    async def list_assets(self, context: SecurityContext, cursor: Optional[str] = None, limit: int = 50) -> CursorPage[AssetSummary]:
        return CursorPage(
            items=[],
            next_cursor=None,
            has_more=False
        )

    async def get_asset_details(self, asset_id: str, context: SecurityContext) -> AssetDetailResponse:
        return AssetDetailResponse(
            id=asset_id,
            name="Unknown Asset",
            health_status="UNKNOWN",
            processing_status="IDLE",
            last_updated=None, # type: ignore
            document_count=0
        )

    async def list_asset_facts(self, asset_id: str, context: SecurityContext, cursor: Optional[str] = None, limit: int = 50) -> CursorPage[FactSummary]:
        return CursorPage(
            items=[],
            next_cursor=None,
            has_more=False
        )

    async def list_asset_findings(self, asset_id: str, context: SecurityContext, cursor: Optional[str] = None, limit: int = 50) -> CursorPage[FindingSummary]:
        return CursorPage(
            items=[],
            next_cursor=None,
            has_more=False
        )
