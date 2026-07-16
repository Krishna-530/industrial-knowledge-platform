import time
import logging
from app.storage.service import StorageService
from app.services.document_content_service import DocumentContentService
from app.processing.service import ProcessingService
from app.services.chunking.service import ChunkingService
from core.events.document_uploaded import DocumentUploaded
from core.events.document_processed import DocumentProcessed
from core.event_bus.publisher import EventPublisher

logger = logging.getLogger(__name__)

from app.services.graph_service import KnowledgeGraphService
from core.settings import Settings

class DocumentProcessingWorkflow:
    def __init__(
        self,
        storage_service: StorageService,
        content_service: DocumentContentService,
        processing_service: ProcessingService,
        chunking_service: ChunkingService,
        event_publisher: EventPublisher,
        graph_service: KnowledgeGraphService,
        settings: Settings
    ):
        self.storage_service = storage_service
        self.content_service = content_service
        self.processing_service = processing_service
        self.chunking_service = chunking_service
        self.event_publisher = event_publisher
        self.graph_service = graph_service
        self.settings = settings

    async def handle_document_uploaded(self, event: DocumentUploaded) -> None:
        start_time = time.perf_counter()
        logger.info({"event": "workflow_started", "workflow_name": "DocumentProcessingWorkflow", "document_id": str(event.document_id), "version_id": str(event.version_id)})
        
        await self.content_service.create_pending_content(event.version_id)
        await self.content_service.mark_processing_started(event.version_id)
        
        if not event.storage_identifier:
            await self.content_service.mark_processing_failed(event.version_id, "No storage identifier found")
            return
            
        try:
            stream = await self.storage_service.read_file(event.document_id, event.storage_identifier)
            result = await self.processing_service.extract_content(event.mime_type, stream)
            await self.content_service.store_processing_result(event.version_id, result)
            
            # Delegate chunking orchestration and persistence fully to ChunkingService
            chunks = await self.chunking_service.process_document(
                document_id=event.document_id,
                version_id=event.version_id,
                text=result.raw_text,
                base_metadata={"language": result.detected_language} if result.detected_language else {}
            )
            
            # Knowledge Graph Initialization (Phase 14)
            if self.settings.enable_knowledge_graph:
                try:
                    await self.graph_service.initialize_document_graph(
                        document_id=str(event.document_id),
                        title=result.document_metadata.get("title", f"Document {event.document_id}") if result.document_metadata else f"Document {event.document_id}",
                        metadata={"version_id": str(event.version_id), "language": result.detected_language}
                    )
                    
                    # Prepare chunk data for graph
                    chunk_data = [{"chunk_id": str(c.id), "index": c.chunk_index} for c in chunks]
                    await self.graph_service.process_document_chunks(str(event.document_id), chunk_data)
                except Exception as graph_e:
                    logger.warning(f"Knowledge Graph initialization failed, but continuing: {graph_e}")
            
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info({
                "event": "workflow_completed",
                "workflow_name": "DocumentProcessingWorkflow",
                "document_id": str(event.document_id),
                "version_id": str(event.version_id),
                "duration_ms": duration_ms,
                "status": "COMPLETED"
            })
            
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
            logger.info({"event": "chunk_generation_failed", "version_id": str(event.version_id), "error": str(e)})
            await self.content_service.mark_processing_failed(event.version_id, str(e))
