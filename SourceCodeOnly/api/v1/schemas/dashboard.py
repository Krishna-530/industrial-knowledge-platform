from pydantic import BaseModel
from typing import List, Optional, Generic, TypeVar
from datetime import datetime
from uuid import UUID

T = TypeVar('T')

class CursorPage(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[str] = None
    has_more: bool

class DashboardStats(BaseModel):
    total_documents: int
    total_assets: int

class AdminDashboardStats(DashboardStats):
    total_users: int = 0

class KnowledgeGraphStats(BaseModel):
    total_nodes: int
    total_edges: int
    sync_lag: Optional[float] = None
    status: str = "unavailable"

class WorkerQueueStats(BaseModel):
    queued: int
    processing: int
    completed: int
    failed: int
    total: int

class RetrievalStats(BaseModel):
    total_searches: Optional[int] = None
    average_latency: Optional[float] = None
    status: str = "unavailable"

class RecentDocument(BaseModel):
    id: UUID
    title: str
    status: str
    uploaded_at: datetime

class ProcessingQueueItem(BaseModel):
    job_id: UUID
    job_type: str
    status: str
    started_at: Optional[datetime] = None

class DashboardOverviewResponse(BaseModel):
    stats: DashboardStats
    graph: KnowledgeGraphStats
    workers: WorkerQueueStats
    retrieval: RetrievalStats
    recent_documents: List[RecentDocument]
    processing_queue: List[ProcessingQueueItem]

class AdminDashboardOverviewResponse(DashboardOverviewResponse):
    stats: AdminDashboardStats
    active_conflicts: int
    processing_jobs: int
    total_chunks: int = 0
    total_entities: int = 0
    total_relationships: int = 0

class AssetSummary(BaseModel):
    id: str
    name: str
    health_status: str
    last_updated: datetime

class AssetDetailResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    metadata: dict = {}
    health_status: str
    processing_status: str
    last_updated: datetime
    document_count: int
    last_processed: Optional[datetime] = None
    links: List[str] = []

class FactSummary(BaseModel):
    id: UUID
    property_name: str
    value: str
    confidence: float
    source_document_id: UUID

class FindingSummary(BaseModel):
    id: UUID
    finding_type: str
    description: str
    severity: str
    created_at: datetime
