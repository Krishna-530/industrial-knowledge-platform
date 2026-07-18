import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check_db_ok(db_session):
    from database.engine import get_db_session
    app.dependency_overrides[get_db_session] = lambda: db_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
        
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert data["database"]["status"] == "ok"

@pytest.mark.asyncio
async def test_health_check_db_error():
    from database.engine import get_db_session
    
    # Create a dummy session that throws an error when execute is called
    class DummyFailingSession:
        async def execute(self, *args, **kwargs):
            raise Exception("DB connection failed")
            
    app.dependency_overrides[get_db_session] = lambda: DummyFailingSession()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
        
    app.dependency_overrides.clear()
    
    assert response.status_code == 503
    data = response.json()["detail"]
    assert data["status"] == "error"
    assert "database" in data
    assert data["database"]["status"] == "error"
    assert "DB connection failed" in data["database"]["error"]
