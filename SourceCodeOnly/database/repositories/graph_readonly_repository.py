import logging
from typing import Any, Dict, List
from neo4j import AsyncDriver
from neo4j.exceptions import ClientError, TransientError

logger = logging.getLogger(__name__)

class ReadOnlyGraphRepository:
    """
    Dedicated repository for read-only GraphRAG operations.
    Should be instantiated with a Neo4j driver pointing to a Read Replica.
    """
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def execute_read(self, query: str, parameters: Dict[str, Any], timeout_ms: int = 2000) -> List[Dict[str, Any]]:
        # In Neo4j Python driver, we can set transaction timeouts via neo4j.TransactionConfig
        # For simplicity, we just use session.read_transaction or simple execute_query
        try:
            async with self.driver.session(default_access_mode="READ") as session:
                result = await session.run(query, parameters, timeout=timeout_ms/1000.0)
                records = await result.data()
                return records
        except TransientError as e:
            logger.warning(f"Transient Neo4j error during read: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to execute read query against Read Replica: {e}")
            raise
