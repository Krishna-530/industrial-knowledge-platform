import logging
from typing import Optional
from neo4j import AsyncGraphDatabase, AsyncDriver

logger = logging.getLogger(__name__)

class GraphSessionManager:
    """
    Enterprise Neo4j session manager handling read/write routing and connection pooling.
    Repositories should request a session from this manager, never construct their own.
    """
    def __init__(self, uri: str, auth: tuple):
        # In a real enterprise system, routing drivers (neo4j://) handle replica routing
        self.driver: Optional[AsyncDriver] = AsyncGraphDatabase.driver(uri, auth=auth, max_connection_pool_size=50)

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def get_read_session(self):
        """
        Yields a session explicitly requesting the READ replica for Retrieval loads.
        """
        return self.driver.session(default_access_mode="READ")

    async def get_write_session(self):
        """
        Yields a session explicitly requesting the WRITE primary for Outbox syncing.
        """
        return self.driver.session(default_access_mode="WRITE")
        
    async def get_health_status(self) -> bool:
        try:
            async with self.driver.session(default_access_mode="READ") as session:
                await session.run("RETURN 1")
                return True
        except Exception as e:
            logger.error(f"Graph Connection unhealthy: {e}")
            return False
