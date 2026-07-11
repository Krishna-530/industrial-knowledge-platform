import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from database.repositories.user import UserRepository
from database.repositories.role import RoleRepository
from core.security import get_password_hash

@pytest.mark.asyncio
async def test_login_success(db_session: AsyncSession):
    # Setup test user in DB
    user_repo = UserRepository(db_session)
    role_repo = RoleRepository(db_session)
    role = await role_repo.get_by_name("user")
    
    await user_repo.create(
        name="API User",
        email="api@example.com",
        password_hash=get_password_hash("password123"),
        role_id=role.id
    )
    
    # We need to override the dependency to use our test session
    from database.engine import get_db_session
    app.dependency_overrides[get_db_session] = lambda: db_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", json={
            "email": "api@example.com",
            "password": "password123"
        })
        
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
