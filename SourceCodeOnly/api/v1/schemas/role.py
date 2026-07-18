from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: Optional[str] = None

class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    is_system: bool
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = []

class RoleListResponse(BaseModel):
    items: List[RoleResponse]
    total: int
