from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role_id: UUID

class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None

class UpdatePasswordRequest(BaseModel):
    password: str = Field(..., min_length=8)

class UpdateRoleRequest(BaseModel):
    role_id: UUID

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    role_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
