import logging
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from database.repositories.document_content_repository import DocumentContentRepository
from app.processing.base import ProcessingResult
from core.enums.processing_status import ProcessingStatus
from core.exceptions.document import DocumentContentPersistenceException, DocumentContentException

logger = logging.getLogger(__name__)

class DocumentContentService:
    """
    Dedicated service for managing DocumentContent persistence and lifecycle states.
    Owns its own database transactions.
    """
    def __init__(self, session: AsyncSession, repo: DocumentContentRepository):
        self.session = session
        self.repo = repo

    async def create_pending_content(self, document_version_id: UUID) -> None:
        try:
            await self.repo.create(document_version_id=document_version_id)
            await self.session.commit()
            logger.info({"event": "document_content_created", "version_id": str(document_version_id), "status": ProcessingStatus.PENDING})
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error({"event": "document_content_creation_failed", "version_id": str(document_version_id), "error": str(e)})
            raise DocumentContentPersistenceException(message="Failed to create pending document content")

    async def store_processing_result(self, document_version_id: UUID, result: ProcessingResult) -> None:
        try:
            content = await self.repo.get_by_version(document_version_id)
            if not content:
                raise DocumentContentException(message=f"No DocumentContent found for version {document_version_id}")
                
            await self.repo.update(
                content,
                raw_text=result.raw_text,
                page_count=result.page_count,
                word_count=result.word_count,
                character_count=result.character_count,
                document_metadata=result.document_metadata,
                processing_metadata=result.processing_metadata,
                processing_status=ProcessingStatus.COMPLETED,
                processing_finished_at=datetime.now(timezone.utc)
            )
            await self.session.commit()
            logger.info({"event": "document_content_updated", "version_id": str(document_version_id), "status": ProcessingStatus.COMPLETED})
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error({"event": "document_content_update_failed", "version_id": str(document_version_id), "error": str(e)})
            raise DocumentContentPersistenceException(message="Failed to store processing result")

    async def mark_processing_failed(self, document_version_id: UUID, error_message: str) -> None:
        try:
            content = await self.repo.get_by_version(document_version_id)
            if not content:
                return
                
            await self.repo.update(
                content,
                processing_status=ProcessingStatus.FAILED,
                processing_error=error_message,
                processing_finished_at=datetime.now(timezone.utc)
            )
            await self.session.commit()
            logger.info({"event": "document_content_marked_failed", "version_id": str(document_version_id)})
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error({"event": "document_content_mark_failed_error", "version_id": str(document_version_id), "error": str(e)})
            raise DocumentContentPersistenceException(message="Failed to mark processing as failed")

    async def mark_processing_started(self, document_version_id: UUID) -> None:
        try:
            content = await self.repo.get_by_version(document_version_id)
            if content:
                await self.repo.update(
                    content,
                    processing_status=ProcessingStatus.PROCESSING,
                    processing_started_at=datetime.now(timezone.utc)
                )
                await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DocumentContentPersistenceException(message="Failed to mark processing as started")
