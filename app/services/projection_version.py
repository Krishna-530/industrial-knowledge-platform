import logging

logger = logging.getLogger(__name__)

class ProjectionVersionService:
    """
    Provides a monotonic integer representing the current version of the Graph projection.
    Updated every time the GraphSyncWorker drains the Outbox.
    Used for Cache Invalidation.
    """
    def __init__(self):
        # Stubbed. In production, this reads a simple integer from PostgreSQL or Redis.
        self._current_version = 1

    async def get_current_version(self) -> int:
        return self._current_version

    async def increment_version(self) -> int:
        self._current_version += 1
        logger.info(f"Graph Projection Version incremented to {self._current_version}")
        return self._current_version
