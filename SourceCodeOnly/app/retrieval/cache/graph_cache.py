import hashlib
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class GraphQueryCache:
    """
    Tenant-aware cache for Graph Queries, bound to Projection Version.
    """
    def __init__(self):
        # Stubbed dict cache. Production uses Redis.
        self._cache = {}

    def _generate_key(self, tenant_id: str, query: str, params: dict, projection_version: int) -> str:
        payload = json.dumps({
            "t": tenant_id,
            "q": query,
            "p": params,
            "v": projection_version
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    async def get(self, tenant_id: str, query: str, params: dict, projection_version: int) -> Optional[List[Dict[str, Any]]]:
        key = self._generate_key(tenant_id, query, params, projection_version)
        hit = self._cache.get(key)
        if hit:
            logger.debug(f"Graph Cache HIT for {key}")
            return hit
        return None

    async def set(self, tenant_id: str, query: str, params: dict, projection_version: int, result: List[Dict[str, Any]], ttl_seconds: int) -> None:
        key = self._generate_key(tenant_id, query, params, projection_version)
        self._cache[key] = result
        logger.debug(f"Graph Cache SET for {key} (ttl: {ttl_seconds}s)")
