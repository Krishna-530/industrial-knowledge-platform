from fastapi import Depends
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
    provide_processing_service
)

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
    event_publisher: EventPublisher = Depends(provide_event_publisher)
) -> DocumentProcessingWorkflow:
    return DocumentProcessingWorkflow(
        storage_service=storage_service,
        content_service=content_service,
        processing_service=processing_service,
        event_publisher=event_publisher
    )
