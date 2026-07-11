from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
import logging

from database.repositories.user import UserRepository
from database.repositories.role import RoleRepository
from core.security import verify_password, create_access_token, create_refresh_token, verify_token
from core.blacklist import add_to_blacklist, is_blacklisted
from core.exceptions import UnauthorizedError
from api.v1.schemas.auth import Token, UserLogin

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)

    async def login(self, credentials: UserLogin) -> Token:
        user = await self.user_repo.get_by_email(credentials.email)
        
        if not user or not user.is_active or not verify_password(credentials.password, user.password_hash):
            logger.warning(f"Failed login attempt for {credentials.email}")
            raise UnauthorizedError(message="Invalid credentials")
            
        role = await self.role_repo.get_by_id(user.role_id)
        role_name = role.name if role else "User"
            
        payload = {
            "sub": str(user.id),
            "role": role_name
        }
        
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)
        
        logger.info(f"User {credentials.email} logged in successfully")
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, token: str) -> Token:
        if is_blacklisted(token):
            raise UnauthorizedError(message="Token has been blacklisted")
            
        try:
            payload = verify_token(token)
            if payload.get("type") != "refresh":
                raise UnauthorizedError(message="Invalid token type")
                
            user_id = payload.get("sub")
            role = payload.get("role")
            if not user_id or not role:
                raise UnauthorizedError(message="Invalid token payload")
                
        except jwt.PyJWTError:
            raise UnauthorizedError(message="Invalid or expired refresh token")
            
        new_payload = {
            "sub": user_id,
            "role": role
        }
        
        new_access_token = create_access_token(new_payload)
        return Token(
            access_token=new_access_token,
            refresh_token=token,
            token_type="bearer"
        )

    def logout(self, token: str, user_email: str) -> None:
        add_to_blacklist(token)
        logger.info(f"User {user_email} logged out successfully")
