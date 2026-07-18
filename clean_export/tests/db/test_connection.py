import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_db_connection(db_session: AsyncSession):
    """Verify that we can connect to the database and execute a simple query."""
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar()
    assert value == 1
