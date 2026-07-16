from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from core.settings import Settings
from core.security import verify_token
from core.blacklist import is_blacklisted
from core.exceptions import UnauthorizedError, ForbiddenError
from api.v1.schemas.auth import User
from app.security.context import SecurityContext
from app.security.permissions import Permission

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

from database.engine import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.user import UserRepository
from database.repositories.role import RoleRepository
import uuid

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_db_session)
) -> User:
    if is_blacklisted(token):
        raise UnauthorizedError(message="Token has been blacklisted")
        
    try:
        payload = verify_token(token)
        user_id_str: str = payload.get("sub")
        
        if user_id_str is None:
            raise UnauthorizedError(message="Could not validate credentials")
            
        token_type: str = payload.get("type")
        if token_type != "access":
            raise UnauthorizedError(message="Invalid token type")
            
    except jwt.PyJWTError:
        raise UnauthorizedError(message="Could not validate credentials")
        
    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError(message="Invalid user ID format")
        
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_id(user_uuid)
    
    if not user:
        raise UnauthorizedError(message="User not found")
    
    if not user.is_active:
        raise UnauthorizedError(message="User account is deactivated")
        
    role_repo = RoleRepository(db_session)
    role = await role_repo.get_by_id(user.role_id)
    
    if not role:
        raise UnauthorizedError(message="Assigned role no longer exists")
        
    return User(
        user_id=str(user.id),
        email=user.email,
        full_name=user.name,
        role=role.name
    )

async def get_security_context(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
) -> SecurityContext:
    # In a real system, you would fetch workspace and specific permissions from DB
    # For now, we mock permissions based on role
    permissions = []
    if current_user.role.lower() == "admin":
        permissions.append(Permission.ADMIN.value)
    else:
        permissions.extend([
            Permission.READ_DOCUMENT.value,
            Permission.READ_ASSET.value,
            Permission.READ_ANALYTICS.value
        ])
        
    return SecurityContext(
        user=current_user,
        permissions=permissions
    )
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        allowed = [r.lower() for r in self.allowed_roles]
        if current_user.role.lower() not in allowed:
            raise ForbiddenError(message="Operation not permitted")
        return current_user
