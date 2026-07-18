import logging
import asyncio
from database.models.job import Job
from workers.payloads import ProcessingJobPayload, IndexingJobPayload
from app.workflows.document_processing_workflow import DocumentProcessingWorkflow
from app.workflows.indexing_workflow import IndexingWorkflow
from core.events.document_uploaded import DocumentUploaded

logger = logging.getLogger(__name__)

class JobExecutor:
    """
    Decouples the Worker from actual workflow implementations.
    Deserializes strongly-typed payloads and invokes the domain.
    """
    def __init__(
        self, 
        processing_workflow: DocumentProcessingWorkflow, 
        indexing_workflow: IndexingWorkflow,
        job_timeout_seconds: int = 300
    ):
        self.processing_workflow = processing_workflow
        self.indexing_workflow = indexing_workflow
        self.job_timeout_seconds = job_timeout_seconds

    async def execute(self, job: Job) -> None:
        try:
            if job.job_type == "PROCESS_DOCUMENT":
                payload = ProcessingJobPayload(**job.payload)
                event = DocumentUploaded(
                    document_id=payload.document_id,
                    version_id=payload.version_id,
                    version_number=payload.version_number,
                    storage_identifier=payload.storage_identifier,
                    mime_type=payload.mime_type
                )
                
                # Enforce JOB_TIMEOUT
                await asyncio.wait_for(
                    self.processing_workflow.handle_document_uploaded(event),
                    timeout=self.job_timeout_seconds
                )
            elif job.job_type == "INDEX_DOCUMENT":
                payload = IndexingJobPayload(**job.payload)
                await asyncio.wait_for(
                    self.indexing_workflow.handle_document_indexed(payload.version_id),
                    timeout=self.job_timeout_seconds
                )
            else:
                raise ValueError(f"Unknown job_type: {job.job_type}")
        except asyncio.TimeoutError:
            logger.error({"event": "job_execution_timeout", "job_id": str(job.id), "timeout_seconds": self.job_timeout_seconds})
            raise RuntimeError(f"Job execution timed out after {self.job_timeout_seconds} seconds")
        except Exception as e:
            logger.error({"event": "job_execution_error", "job_id": str(job.id), "error": str(e)})
            raise
