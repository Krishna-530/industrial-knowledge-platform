import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.search.interfaces import AbstractSearchProvider
from database.repositories.document_content_repository import DocumentContentRepository
from core.enums.processing_status import ProcessingStatus

logger = logging.getLogger(__name__)

class IndexingService:
    """
    Orchestrates index writes against the underlying search provider.
    Maintains the search index in sync with DocumentContent.
    """
    def __init__(
        self, 
        session: AsyncSession,
        provider: AbstractSearchProvider,
        content_repo: DocumentContentRepository
    ):
        self.session = session
        self.provider = provider
        self.content_repo = content_repo

    async def update_index(self, document_version_id: UUID) -> None:
        """
        Updates the search index for a given document version, and clears older versions.
        Called by the INDEX_DOCUMENT background worker.
        """
        try:
            content_record = await self.content_repo.get_by_version_id(document_version_id)
            if not content_record:
                logger.warning({"event": "indexing_skipped", "reason": "Content not found", "version_id": str(document_version_id)})
                return

            if content_record.processing_status != ProcessingStatus.COMPLETED:
                logger.warning({"event": "indexing_skipped", "reason": "Processing not completed", "version_id": str(document_version_id)})
                return
                
            raw_text = content_record.raw_text or ""
            language = content_record.language or "english"
            document_id = content_record.document_version.document_id

            logger.info({"event": "indexing_started", "document_id": str(document_id), "version_id": str(document_version_id)})

            # The provider performs updates inside the same transaction as this service
            await self.provider.clear_previous_versions(document_id, document_version_id)
            await self.provider.update_document(
                document_version_id=document_version_id,
                content=raw_text,
                language=language,
                metadata={}
            )
            
            await self.session.commit()
            logger.info({"event": "indexing_completed", "document_id": str(document_id), "version_id": str(document_version_id)})
        except Exception as e:
            await self.session.rollback()
            logger.error({"event": "indexing_failed", "version_id": str(document_version_id), "error": str(e)})
            raise

    async def trigger_full_rebuild(self) -> None:
        """
        Triggers a full rebuild of the search index from the source of truth.
        """
        try:
            await self.provider.rebuild_index()
            await self.session.commit()
            logger.info({"event": "index_rebuild_completed"})
        except Exception as e:
            await self.session.rollback()
            logger.error({"event": "index_rebuild_failed", "error": str(e)})
            raise
