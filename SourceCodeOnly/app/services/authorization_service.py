from typing import List
from uuid import UUID
from app.retrieval.schemas import SearchHit

class AuthorizationService:
    """
    Evaluates permissions for a list of SearchHits based on the requesting user's roles.
    """
    async def filter_authorized_hits(self, user_id: UUID, roles: List[str], hits: List[SearchHit]) -> List[SearchHit]:
        """
        Stage 2: Filters out hits the user is not allowed to see.
        For now, this assumes basic access is granted by default, but provides the hook
        for enterprise RBAC integration (e.g., checking document categories against user roles).
        """
        # In a full RBAC implementation, we would check if user_id is the owner,
        # or if the document's category allows access for `roles`.
        # For this foundation, we pass through all hits.
        return hits
