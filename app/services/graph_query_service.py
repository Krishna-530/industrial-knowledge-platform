import logging
from typing import Dict, Any, List, Optional
from database.repositories.graph_readonly_repository import ReadOnlyGraphRepository

logger = logging.getLogger(__name__)

class GraphQueryService:
    """
    Handles read-only graph explorations for the UI Explorer.
    (Different from GraphTraversalEngine which handles deep RAG subgraph extraction).
    """
    def __init__(self, readonly_repo: ReadOnlyGraphRepository):
        self.repo = readonly_repo

    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        query = "MATCH (n {id: $node_id}) RETURN n"
        records = await self.repo.execute_read(query, {"node_id": node_id})
        if not records:
            return None
        node = records[0]["n"]
        return {"id": node.get("id", node_id), "labels": list(node.labels), "properties": dict(node)}

    async def get_neighborhood(self, node_id: str, depth: int = 1) -> Dict[str, Any]:
        # Simple 1-hop neighborhood for UI expansion
        query = """
        MATCH (c {id: $node_id})-[r]-(n)
        RETURN c, r, n LIMIT 100
        """
        records = await self.repo.execute_read(query, {"node_id": node_id})
        
        nodes = {}
        edges = []
        center_node = None
        
        for record in records:
            c = record["c"]
            n = record["n"]
            r = record["r"]
            
            if not center_node:
                center_node = {"id": c.get("id"), "labels": list(c.labels), "properties": dict(c)}
                nodes[c.get("id")] = center_node
                
            n_data = {"id": n.get("id"), "labels": list(n.labels), "properties": dict(n)}
            nodes[n.get("id")] = n_data
            
            edges.append({
                "id": str(r.element_id),
                "start_node_id": c.get("id") if r.start_node == c else n.get("id"),
                "end_node_id": n.get("id") if r.end_node == n else c.get("id"),
                "type": r.type,
                "properties": dict(r),
                "provenance": None
            })
            
        return {
            "center_node": center_node or await self.get_node(node_id),
            "nodes": list(nodes.values()),
            "edges": edges
        }

    async def search_nodes(self, text: str, limit: int = 50) -> Dict[str, Any]:
        # Substring search on name for UI autocomplete
        query = """
        MATCH (n) WHERE toLower(n.name) CONTAINS toLower($text)
        RETURN n LIMIT toInteger($limit)
        """
        records = await self.repo.execute_read(query, {"text": text, "limit": limit})
        nodes = []
        for record in records:
            n = record["n"]
            nodes.append({"id": n.get("id"), "labels": list(n.labels), "properties": dict(n)})
        return {"nodes": nodes, "edges": []}

    async def get_statistics(self) -> Dict[str, Any]:
        if not self.repo:
            return {"total_nodes": 0, "total_edges": 0, "lag_seconds": None, "active_tenants": None}
        query = """
        CALL { MATCH (n) RETURN count(n) AS total_nodes }
        CALL { MATCH ()-[r]->() RETURN count(r) AS total_edges }
        RETURN total_nodes, total_edges
        """
        records = await self.repo.execute_read(query, {})
        if not records:
            return {"total_nodes": 0, "total_edges": 0, "lag_seconds": None, "active_tenants": None}
            
        return {
            "total_nodes": records[0]["total_nodes"],
            "total_edges": records[0]["total_edges"],
            "lag_seconds": None,
            "active_tenants": None
        }

    async def get_relationship_evidence(self, relationship_id: str) -> Dict[str, Any]:
        # Query Neo4j to find the relationship by elementId, then find chunks that mention both entities
        query = """
        MATCH (sub:Entity)-[r]->(obj:Entity)
        WHERE elementId(r) = $rel_id
        MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)-[:MENTIONS]->(sub)
        MATCH (c)-[:MENTIONS]->(obj)
        RETURN sub, r, obj, c, d.id AS document_id
        """
        records = await self.repo.execute_read(query, {"rel_id": relationship_id})
        
        traces = []
        chunks = []
        confidence_score = 1.0
        
        for record in records:
            r = record["r"]
            c = record["c"]
            doc_id = record["document_id"]
            confidence_score = r.get("quality_score", 1.0)
            
            chunks.append({
                "chunk_id": c.get("id"),
                "document_id": doc_id,
                "text_snippet": c.get("text", "")[:500],
                "score": confidence_score
            })
            
        traces.append({
            "id": f"prov_{relationship_id}",
            "relationship_id": relationship_id,
            "confidence_score": confidence_score,
            "supporting_chunks": chunks
        })
        
        return {"traces": traces}
