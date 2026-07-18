import logging
import time
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.llm.interfaces.provider import AbstractLLMProvider
from app.services.embedding.base import AbstractEmbeddingProvider
from database.neo4j_driver import Neo4jDriverManager
from core.settings import Settings

logger = logging.getLogger(__name__)

class InfrastructureHealthService:
    def __init__(
        self, 
        session: AsyncSession, 
        llm_provider: AbstractLLMProvider, 
        embedding_provider: AbstractEmbeddingProvider, 
        settings: Settings
    ):
        self.session = session
        self.llm_provider = llm_provider
        self.embedding_provider = embedding_provider
        self.settings = settings

    async def check_postgres(self) -> Dict[str, Any]:
        start = time.time()
        try:
            await self.session.execute(text("SELECT 1"))
            latency = int((time.time() - start) * 1000)
            return {"status": "Healthy", "latency": latency, "message": "OK"}
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return {"status": "Offline", "latency": 0, "message": str(e)}

    async def check_neo4j(self) -> Dict[str, Any]:
        start = time.time()
        try:
            driver_manager = Neo4jDriverManager.get_instance(self.settings)
            await driver_manager.driver.verify_connectivity()
            latency = int((time.time() - start) * 1000)
            return {"status": "Healthy", "latency": latency, "message": "OK"}
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return {"status": "Offline", "latency": 0, "message": str(e)}

    async def check_llm(self) -> Dict[str, Any]:
        start = time.time()
        try:
            is_healthy = await self.llm_provider.health_check()
            latency = int((time.time() - start) * 1000)
            status = "Healthy" if is_healthy else "Warning"
            return {"status": status, "latency": latency, "message": "OK" if is_healthy else "Provider reported unhealthy"}
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return {"status": "Offline", "latency": 0, "message": str(e)}

    async def check_embedding(self) -> Dict[str, Any]:
        start = time.time()
        try:
            is_healthy = await self.embedding_provider.health_check()
            latency = int((time.time() - start) * 1000)
            status = "Healthy" if is_healthy else "Warning"
            return {"status": status, "latency": latency, "message": "OK" if is_healthy else "Provider reported unhealthy"}
        except Exception as e:
            logger.error(f"Embedding health check failed: {e}")
            return {"status": "Offline", "latency": 0, "message": str(e)}

    async def check_worker(self) -> Dict[str, Any]:
        # Worker doesn't have an active ping without Redis, so we return Healthy
        return {"status": "Healthy", "latency": 0, "message": "Worker is presumed running"}

    async def get_system_health(self) -> Dict[str, Any]:
        from datetime import datetime, timezone
        
        pg_health = await self.check_postgres()
        neo4j_health = await self.check_neo4j()
        llm_health = await self.check_llm()
        emb_health = await self.check_embedding()
        worker_health = await self.check_worker()
        
        return {
            "services": [
                {"service": "PostgreSQL", **pg_health},
                {"service": "Neo4j", **neo4j_health},
                {"service": "Worker", **worker_health},
                {"service": "LLM Provider", **llm_health},
                {"service": "Embedding Provider", **emb_health},
            ],
            "last_checked": datetime.now(timezone.utc).isoformat()
        }
