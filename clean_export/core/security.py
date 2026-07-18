from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from core.settings import Settings

settings = Settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": token_type})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_access_token(data: dict) -> str:
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    return create_token(data, expires_delta, "access")

def create_refresh_token(data: dict) -> str:
    expires_delta = timedelta(minutes=settings.refresh_token_expire_minutes)
    return create_token(data, expires_delta, "refresh")

def verify_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
