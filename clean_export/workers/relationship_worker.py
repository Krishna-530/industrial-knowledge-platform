import asyncio
import logging
from typing import List, Protocol, Optional
from database.models.job import Job
from workers.entity_worker import WorkerQueue

logger = logging.getLogger(__name__)

class RelationshipExecutionBoundary(Protocol):
    async def execute_job(self, job: Job) -> None: ...

class RelationshipWorker:
    def __init__(
        self,
        worker_id: str,
        supported_types: List[str],
        execution_boundary: RelationshipExecutionBoundary,
        queue: WorkerQueue,
        poll_interval: float = 2.0,
        backoff_multiplier: int = 10
    ):
        self.worker_id = worker_id
        self.supported_types = supported_types
        self.execution_boundary = execution_boundary
        self.queue = queue
        self.poll_interval = poll_interval
        self.backoff_multiplier = backoff_multiplier
        self._running = False
        self._task = None

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info({"event": "worker_started", "worker_id": self.worker_id})

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info({"event": "worker_stopped", "worker_id": self.worker_id})

    async def _run_loop(self):
        while self._running:
            try:
                await self._process_next_job()
            except Exception as e:
                logger.error({"event": "worker_loop_error", "worker_id": self.worker_id, "error": str(e)})
            
            await asyncio.sleep(self.poll_interval)

    async def _process_next_job(self):
        job = await self.queue.dequeue(self.supported_types, worker_id=self.worker_id)
        
        if not job:
            return 
            
        try:
            await self.execution_boundary.execute_job(job)
            await self.queue.mark_completed(job.id, worker_id=self.worker_id)
        except Exception as e:
            await self.queue.mark_failed(job.id, str(e), worker_id=self.worker_id, backoff_multiplier=self.backoff_multiplier)
