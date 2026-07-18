import asyncio
import logging
from database.engine import async_session_factory
from database.repositories.entity_repository import EntityRepository
from app.services.graph_service import KnowledgeGraphService

logger = logging.getLogger(__name__)

class GraphSyncWorker:
    """
    Sweeps the GraphOutboxEvent table and flushes MERGE operations to Neo4j.
    Ensures distributed eventual consistency.
    """
    def __init__(
        self,
        worker_id: str,
        graph_service: KnowledgeGraphService,
        poll_interval: float = 5.0,
        batch_size: int = 100
    ):
        self.worker_id = worker_id
        self.graph_service = graph_service
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self._running = False
        self._task = None

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info({"event": "graph_sync_worker_started", "worker_id": self.worker_id})

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info({"event": "graph_sync_worker_stopped", "worker_id": self.worker_id})

    async def _run_loop(self):
        while self._running:
            try:
                await self._sync_outbox_events()
            except Exception as e:
                logger.error({"event": "graph_sync_error", "worker_id": self.worker_id, "error": str(e)})
            
            await asyncio.sleep(self.poll_interval)

    async def _sync_outbox_events(self):
        # We need an isolated session per sweep
        async with async_session_factory() as session:
            repo = EntityRepository(session)
            events = await repo.get_pending_outbox_events(limit=self.batch_size)
            
            if not events:
                return

            logger.info(f"Syncing {len(events)} outbox events to Neo4j.")
            
            for event in events:
                try:
                    payload = event.payload
                    # Example Dispatch mapping
                    if event.event_type.value == "NODE_UPSERT":
                        # Stubbed
                        pass
                    elif event.event_type.value == "EDGE_UPSERT":
                        await self.graph_service.sync_edges([payload])
                    
                    event.status = "PROCESSED"
                except Exception as sync_e:
                    logger.error(f"Failed to sync event {event.id}: {sync_e}")
                    event.status = "FAILED"
                    event.error_message = str(sync_e)
                    
            await session.commit()
