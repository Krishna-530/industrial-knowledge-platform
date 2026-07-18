import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.auth import Token, UserLogin
from dependencies.auth import oauth2_scheme, get_current_user
from database.engine import get_db_session
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db_session: AsyncSession = Depends(get_db_session)):
    auth_service = AuthService(db_session)
    return await auth_service.login(credentials)

@router.post("/refresh", response_model=Token)
async def refresh_token(token: str = Depends(oauth2_scheme), db_session: AsyncSession = Depends(get_db_session)):
    auth_service = AuthService(db_session)
    return await auth_service.refresh(token)

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), current_user = Depends(get_current_user), db_session: AsyncSession = Depends(get_db_session)):
    auth_service = AuthService(db_session)
    auth_service.logout(token, current_user.email)
    return {"message": "Successfully logged out"}

