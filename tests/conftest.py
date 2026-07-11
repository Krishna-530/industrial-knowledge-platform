import os
import pytest
import pytest_asyncio
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from alembic.config import Config
from alembic import command
from database.models.base import Base

@pytest.fixture(scope="session")
def postgres_container():
    """Starts a Postgres container for the entire test session."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        # Generate the async URL (testcontainers gives sync psycopg2 by default)
        conn_url = postgres.get_connection_url()
        async_url = conn_url.replace("postgresql+psycopg2", "postgresql+asyncpg")
        # Ensure our tests use this URL by overriding the environment
        os.environ["DATABASE_URL"] = async_url
        yield async_url

@pytest_asyncio.fixture(scope="session")
async def db_engine(postgres_container):
    """Creates an async engine bound to the testcontainer."""
    engine = create_async_engine(postgres_container, pool_pre_ping=True)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session", autouse=True)
def setup_database(postgres_container):
    """Runs Alembic migrations to set up the schema and seed data."""
    # We need to run alembic synchronously using the testcontainer URL
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_container)
    command.upgrade(alembic_cfg, "head")
    yield
    # Optionally, we could downgrade here, but the container dies anyway.

@pytest_asyncio.fixture
async def db_session(db_engine):
    """Provides a fresh database session for a test."""
    async_session = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
        await session.rollback() # Ensure tests don't leak state (though the container is fresh)
