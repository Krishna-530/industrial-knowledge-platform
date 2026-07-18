import logging
from workers.document_worker import DocumentWorker
from workers.entity_worker import EntityWorker
from workers.relationship_worker import RelationshipWorker
from workers.graph_sync_worker import GraphSyncWorker
from core.settings import Settings

logger = logging.getLogger(__name__)

class WorkerManager:
    """
    Coordinates lifecycle of background workers.
    Fully agnostic to what the workers do and how they are constructed.
    """
    def __init__(
        self, 
        settings: Settings, 
        document_worker: DocumentWorker,
        entity_worker: EntityWorker,
        relationship_worker: RelationshipWorker,
        graph_sync_worker: GraphSyncWorker
    ):
        self.settings = settings
        self.workers = [document_worker, entity_worker, relationship_worker, graph_sync_worker]

    async def start_all(self):
        logger.info({"event": "worker_manager_starting", "worker_id": self.settings.worker_id})
        for worker in self.workers:
            await worker.start()

    async def stop_all(self):
        logger.info({"event": "worker_manager_stopping", "worker_id": self.settings.worker_id})
        for worker in self.workers:
            await worker.stop()
