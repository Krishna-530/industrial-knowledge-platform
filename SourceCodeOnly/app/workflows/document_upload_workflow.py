import time
import logging
from uuid import UUID
from typing import AsyncGenerator, Optional

from app.services.document_service import DocumentService
from app.storage.service import StorageService
from core.event_bus.publisher import EventPublisher
from core.events.document_uploaded import DocumentUploaded

logger = logging.getLogger(__name__)

class DocumentUploadWorkflow:
    """
    Orchestrates the entire upload use case using dependency injection.
    """
    def __init__(self, document_service: DocumentService, storage_service: StorageService, event_publisher: EventPublisher):
        self.document_service = document_service
        self.storage_service = storage_service
        self.event_publisher = event_publisher

    async def execute(self, document_id: UUID, user_id: UUID, file_stream: AsyncGenerator[bytes, None], content_type: str, content_length: Optional[int] = None):
        start_time = time.perf_counter()
        logger.info({"event": "workflow_started", "workflow_name": "DocumentUploadWorkflow", "document_id": str(document_id)})
        
        try:
            # 1. Validate & Lock Domain
            doc = await self.document_service.validate_and_lock_for_upload(document_id, content_length)
            next_version = doc.current_version + 1
            
            # 2. Store Bytes
            storage_identifier, bytes_written, checksum = await self.storage_service.save_file(
                document_id=document_id,
                file_stream=file_stream
            )
            
            # 3. Create Version
            try:
                version = await self.document_service.create_document_version(
                    document_id=document_id,
                    version_number=next_version,
                    user_id=user_id,
                    storage_identifier=storage_identifier,
                    checksum=checksum
                )
            except Exception as e:
                # If DB fails to create version, clean up storage
                await self.storage_service.delete_file(document_id, storage_identifier)
                raise e
                
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info({
                "event": "workflow_completed",
                "workflow_name": "DocumentUploadWorkflow",
                "document_id": str(document_id),
                "version_id": str(version.id),
                "duration_ms": duration_ms,
                "status": "COMPLETED"
            })
            
            # 4. Logical Event Handoff via Publisher
            event = DocumentUploaded(
                document_id=document_id,
                version_id=version.id,
                version_number=next_version,
                storage_identifier=storage_identifier,
                mime_type=content_type
            )
            await self.event_publisher.publish(event)
            
            return version
            
        except Exception as e:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error({
                "event": "workflow_failed",
                "workflow_name": "DocumentUploadWorkflow",
                "document_id": str(document_id),
                "duration_ms": duration_ms,
                "status": "FAILED",
                "error_reason": str(e)
            })
            raise
