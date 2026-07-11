from typing import Callable, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import async_session_maker

from core.settings import Settings
from api.v1.dependencies.settings import provide_settings
from api.v1.dependencies.services import provide_storage_service

from database.repositories.document_content_repository import DocumentContentRepository
from app.services.document_content_service import DocumentContentService
from app.processing.service import ProcessingService
from app.workflows.document_processing_workflow import DocumentProcessingWorkflow
from app.services.job_service import JobService
from database.models.job import Job

from workers.job_executor import JobExecutor
from workers.execution_boundary import ExecutionBoundary
from workers.document_worker import DocumentWorker
from workers.manager import WorkerManager

def provide_job_executor_factory() -> Callable[[AsyncSession], JobExecutor]:
    def factory(session: AsyncSession) -> JobExecutor:
        settings = provide_settings()
        storage_service = provide_storage_service(settings)
        content_repo = DocumentContentRepository(session)
        content_service = DocumentContentService(session, content_repo)
        processing_service = ProcessingService()
        
        from api.v1.dependencies.services import provide_event_publisher
        event_publisher = provide_event_publisher()
        
        workflow = DocumentProcessingWorkflow(
            storage_service=storage_service,
            content_service=content_service,
            processing_service=processing_service,
            event_publisher=event_publisher
        )
        
        from app.search.providers.postgres import PostgresSearchProvider
        from app.search.indexing_service import IndexingService
        from app.workflows.indexing_workflow import IndexingWorkflow
        
        search_provider = PostgresSearchProvider(session)
        indexing_service = IndexingService(session, search_provider, content_repo)
        indexing_workflow = IndexingWorkflow(indexing_service)
        
        return JobExecutor(
            processing_workflow=workflow,
            indexing_workflow=indexing_workflow,
            job_timeout_seconds=settings.worker_job_timeout_seconds
        )
    return factory

def provide_execution_boundary() -> ExecutionBoundary:
    return ExecutionBoundary(executor_factory=provide_job_executor_factory())

class SqlWorkerQueue:
    """Adapts JobService to the WorkerQueue protocol without leaking SQL session."""
    async def dequeue(self, supported_types: List[str], worker_id: str) -> Optional[Job]:
        async with async_session_maker() as session:
            return await JobService(session).dequeue(supported_types, worker_id)
            
    async def mark_completed(self, job_id, worker_id: str) -> None:
        async with async_session_maker() as session:
            await JobService(session).mark_completed(job_id, worker_id)
            
    async def mark_failed(self, job_id, error_message: str, worker_id: str, backoff_multiplier: int) -> None:
        async with async_session_maker() as session:
            await JobService(session).mark_failed(job_id, error_message, worker_id, backoff_multiplier)

def provide_worker_queue() -> SqlWorkerQueue:
    return SqlWorkerQueue()

def provide_document_worker() -> DocumentWorker:
    settings = provide_settings()
    return DocumentWorker(
        worker_id=settings.worker_id,
        supported_types=["PROCESS_DOCUMENT"],
        execution_boundary=provide_execution_boundary(),
        queue=provide_worker_queue(),
        poll_interval=settings.worker_poll_interval,
        backoff_multiplier=settings.worker_backoff_multiplier
    )

def provide_worker_manager() -> WorkerManager:
    return WorkerManager(
        settings=provide_settings(),
        document_worker=provide_document_worker()
    )
