import logging
from typing import Optional
from neo4j import AsyncGraphDatabase, AsyncDriver
from core.settings import Settings

logger = logging.getLogger(__name__)

class Neo4jDriverManager:
    """
    Singleton manager for the Neo4j AsyncDriver.
    Ensures that only one driver connection pool is created per application lifecycle.
    """
    _instance: Optional['Neo4jDriverManager'] = None
    
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver: Optional[AsyncDriver] = None

    @classmethod
    def get_instance(cls, settings: Settings) -> 'Neo4jDriverManager':
        if cls._instance is None:
            cls._instance = cls(
                uri=settings.neo4j_uri,
                user=settings.neo4j_user,
                password=settings.neo4j_password
            )
        return cls._instance
        
    async def connect(self):
        if not self._driver:
            logger.info("Initializing Neo4j AsyncDriver...")
            self._driver = AsyncGraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            # Verify connectivity
            try:
                await self._driver.verify_connectivity()
                logger.info("Neo4j connectivity verified.")
            except Exception as e:
                logger.error(f"Failed to verify Neo4j connectivity: {e}")
                raise

    async def close(self):
        if self._driver:
            await self._driver.close()
            self._driver = None
            logger.info("Neo4j AsyncDriver closed.")

    @property
    def driver(self) -> AsyncDriver:
        if not self._driver:
            raise RuntimeError("Neo4j driver is not initialized. Call connect() first.")
        return self._driver
