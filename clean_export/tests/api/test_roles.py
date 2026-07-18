import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from app.main import app
from dependencies.auth import get_current_user
from api.v1.schemas.auth import User as CurrentUser

@pytest.fixture
def mock_admin_user():
    def _mock():
        return CurrentUser(
            user_id=str(uuid4()),
            email="admin@example.com",
            full_name="Admin User",
            role="Admin"
        )
    return _mock

@pytest.mark.asyncio
async def test_list_roles(db_session, mock_admin_user):
    from database.engine import get_db_session
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_current_user] = mock_admin_user
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/roles")
        
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0
    assert "permissions" in data["items"][0]
