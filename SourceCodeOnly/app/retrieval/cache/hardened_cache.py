import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable, Awaitable
from app.retrieval.cache.graph_cache import GraphQueryCache

logger = logging.getLogger(__name__)

class HardenedGraphCache:
    """
    Enterprise cache wrapper protecting Neo4j from thundering herd / cache stampede.
    Implements SingleFlight pattern.
    """
    def __init__(self, base_cache: GraphQueryCache):
        self.cache = base_cache
        self._inflight: Dict[str, asyncio.Event] = {}
        self._inflight_results: Dict[str, Any] = {}

    async def get_or_execute(
        self, 
        tenant_id: str, 
        query: str, 
        params: dict, 
        projection_version: int, 
        ttl_seconds: int,
        execute_fn: Callable[[], Awaitable[List[Dict[str, Any]]]]
    ) -> List[Dict[str, Any]]:
        
        key = self.cache._generate_key(tenant_id, query, params, projection_version)
        
        # 1. Try Cache
        cached = await self.cache.get(tenant_id, query, params, projection_version)
        if cached is not None:
            return cached
            
        # 2. SingleFlight Locking (Stampede Prevention)
        if key in self._inflight:
            logger.debug(f"Cache stampede prevented for key {key}. Waiting for in-flight query...")
            event = self._inflight[key]
            await event.wait()
            # The query has finished, fetch from the result dict
            return self._inflight_results.get(key, [])
            
        # 3. We are the leader, create the event lock
        event = asyncio.Event()
        self._inflight[key] = event
        
        try:
            # 4. Execute the heavy DB query
            logger.debug(f"Leader executing query for key {key}...")
            result = await execute_fn()
            
            # 5. Populate cache and shared inflight results
            await self.cache.set(tenant_id, query, params, projection_version, result, ttl_seconds)
            self._inflight_results[key] = result
            
            return result
        finally:
            # 6. Release waiting requests and cleanup
            event.set()
            self._inflight.pop(key, None)
            self._inflight_results.pop(key, None)
