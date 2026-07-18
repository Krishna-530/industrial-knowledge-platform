from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from api.v1.schemas.auth import User

class SecurityContext(BaseModel):
    """
    Unified security context representing the authenticated principal.
    Separates the authorization boundaries from the raw User entity.
    """
    user: User
    permissions: List[str]
    workspace_id: Optional[UUID] = None
    
    @property
    def is_admin(self) -> bool:
        return self.user.role == "Admin"
