import logging
from uuid import UUID
from app.search.indexing_service import IndexingService

logger = logging.getLogger(__name__)

class IndexingWorkflow:
    """
    Orchestrates the indexing process triggered by the background worker.
    """
    def __init__(self, indexing_service: IndexingService, document_service: "DocumentService"):
        self.indexing_service = indexing_service
        self.document_service = document_service

    async def handle_document_indexed(self, document_id: UUID, document_version_id: UUID) -> None:
        logger.info({"event": "workflow_started", "workflow_name": "IndexingWorkflow", "version_id": str(document_version_id)})
        await self.indexing_service.update_index(document_version_id)
        await self.document_service.activate_document(document_id)
        logger.info({"event": "workflow_completed", "workflow_name": "IndexingWorkflow", "version_id": str(document_version_id)})
