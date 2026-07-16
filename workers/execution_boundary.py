from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import async_session_factory
from workers.job_executor import JobExecutor
from database.models.job import Job
import logging

logger = logging.getLogger(__name__)

class ExecutionBoundary:
    """
    Encapsulates the SQLAlchemy session lifecycle for a single job execution.
    Isolates infrastructure workers from database connectivity.
    """
    def __init__(self, executor_factory: Callable[[AsyncSession], JobExecutor]):
        self.executor_factory = executor_factory
        
    async def execute_job(self, job: Job):
        async with async_session_factory() as session:
            try:
                executor = self.executor_factory(session)
                await executor.execute(job)
            except Exception as e:
                logger.error({"event": "execution_boundary_failed", "job_id": str(job.id), "error": str(e)})
                raise
