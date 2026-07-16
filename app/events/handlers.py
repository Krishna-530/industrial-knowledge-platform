import logging
from core.events.document_uploaded import DocumentUploaded
from database.engine import async_session_factory
from app.services.job_service import JobService
from workers.payloads import ProcessingJobPayload

logger = logging.getLogger(__name__)

async def handle_document_uploaded(event: DocumentUploaded) -> None:
    async with async_session_factory() as session:
        job_service = JobService(session)
        payload = ProcessingJobPayload(
            document_id=event.document_id,
            version_id=event.version_id,
            version_number=event.version_number,
            storage_identifier=event.storage_identifier,
            mime_type=event.mime_type
        )
        try:
            await job_service.enqueue(
                job_type="PROCESS_DOCUMENT",
                payload=payload.model_dump(mode="json")
            )
        except Exception as e:
            logger.error({"event": "event_handler_failed", "handler": "handle_document_uploaded", "error": str(e)})

from core.events.document_processed import DocumentProcessed
from workers.payloads import IndexingJobPayload

async def handle_document_processed(event: DocumentProcessed) -> None:
    async with async_session_factory() as session:
        job_service = JobService(session)
        payload = IndexingJobPayload(
            document_id=event.document_id,
            version_id=event.document_version_id,
            version_number=event.version_number
        )
        try:
            await job_service.enqueue(
                job_type="INDEX_DOCUMENT",
                payload=payload.model_dump(mode="json")
            )
        except Exception as e:
            logger.error({"event": "event_handler_failed", "handler": "handle_document_processed", "error": str(e)})
