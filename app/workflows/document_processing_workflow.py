import time
import logging
from typing import Optional
from app.storage.service import StorageService
from app.services.document_content_service import DocumentContentService
from app.processing.service import ProcessingService
from core.events.document_uploaded import DocumentUploaded
from core.events.document_processed import DocumentProcessed
from core.event_bus.publisher import EventPublisher

logger = logging.getLogger(__name__)

class DocumentProcessingWorkflow:
    """
    Acts as the logical event handler for 'DocumentUploaded'.
    """
    def __init__(
        self,
        storage_service: StorageService,
        content_service: DocumentContentService,
        processing_service: ProcessingService,
        event_publisher: EventPublisher
    ):
        self.storage_service = storage_service
        self.content_service = content_service
        self.processing_service = processing_service
        self.event_publisher = event_publisher

    async def handle_document_uploaded(self, event: DocumentUploaded) -> None:
        start_time = time.perf_counter()
        logger.info({"event": "workflow_started", "workflow_name": "DocumentProcessingWorkflow", "document_id": str(event.document_id), "version_id": str(event.version_id)})
        
        # 1. Create Pending Content
        await self.content_service.create_pending_content(event.version_id)
        await self.content_service.mark_processing_started(event.version_id)
        
        if not event.storage_identifier:
            await self.content_service.mark_processing_failed(event.version_id, "No storage identifier found")
            return
            
        try:
            # 2. Retrieve Stream
            stream = await self.storage_service.read_file(event.document_id, event.storage_identifier)
            
            # 3. Extract
            result = await self.processing_service.extract_content(event.mime_type, stream)
            
            # 4. Store Result
            await self.content_service.store_processing_result(event.version_id, result)
            
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info({
                "event": "workflow_completed",
                "workflow_name": "DocumentProcessingWorkflow",
                "document_id": str(event.document_id),
                "version_id": str(event.version_id),
                "duration_ms": duration_ms,
                "status": "COMPLETED"
            })
            
            # 5. Publish DocumentProcessed to trigger indexing
            await self.event_publisher.publish(
                DocumentProcessed(
                    document_id=event.document_id,
                    document_version_id=event.version_id,
                    version_number=event.version_number
                )
            )
            
        except Exception as e:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error({
                "event": "workflow_failed",
                "workflow_name": "DocumentProcessingWorkflow",
                "document_id": str(event.document_id),
                "version_id": str(event.version_id),
                "duration_ms": duration_ms,
                "status": "FAILED",
                "error_reason": str(e)
            })
            # Record failure state without failing the parent workflow
            await self.content_service.mark_processing_failed(event.version_id, str(e))
