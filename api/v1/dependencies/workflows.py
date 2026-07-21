from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import get_db_session
from app.workflows.document_upload_workflow import DocumentUploadWorkflow
from app.workflows.document_processing_workflow import DocumentProcessingWorkflow

from app.services.document_service import DocumentService
from app.storage.service import StorageService
from app.services.document_content_service import DocumentContentService
from app.processing.service import ProcessingService
from core.event_bus.publisher import EventPublisher

from api.v1.dependencies.services import (
    provide_document_service, 
    provide_storage_service, 
    provide_event_publisher,
    provide_content_service,
    provide_processing_service,
    provide_graph_service
)
from api.v1.dependencies.settings import provide_settings
from core.settings import Settings
from app.services.graph_service import KnowledgeGraphService
from app.services.chunking.service import ChunkingService
from api.v1.dependencies.chunking import provide_chunking_service

def provide_document_upload_workflow(
    document_service: DocumentService = Depends(provide_document_service),
    storage_service: StorageService = Depends(provide_storage_service),
    publisher: EventPublisher = Depends(provide_event_publisher)
) -> DocumentUploadWorkflow:
    return DocumentUploadWorkflow(
        document_service=document_service,
        storage_service=storage_service,
        event_publisher=publisher
    )

def provide_document_processing_workflow(
    storage_service: StorageService = Depends(provide_storage_service),
    content_service: DocumentContentService = Depends(provide_content_service),
    processing_service: ProcessingService = Depends(provide_processing_service),
    chunking_service: ChunkingService = Depends(provide_chunking_service),
    event_publisher: EventPublisher = Depends(provide_event_publisher),
    graph_service: KnowledgeGraphService = Depends(provide_graph_service),
    document_service: DocumentService = Depends(provide_document_service),
    settings: Settings = Depends(provide_settings),
    session: AsyncSession = Depends(get_db_session),
) -> DocumentProcessingWorkflow:
    from app.services.job_service import JobService
    job_service = JobService(session)
    return DocumentProcessingWorkflow(
        storage_service=storage_service,
        content_service=content_service,
        processing_service=processing_service,
        chunking_service=chunking_service,
        event_publisher=event_publisher,
        graph_service=graph_service,
        job_service=job_service,
        document_service=document_service,
        settings=settings,
    )
