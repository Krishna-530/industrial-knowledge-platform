import asyncio
from sqlalchemy import text
from database.engine import async_session_factory
from core.settings import Settings

async def verify_db():
    settings = Settings()
    print(f"DATABASE_URL configured as: {settings.database_url}")
    
    async with async_session_factory() as session:
        # DB version
        ver = await session.execute(text("SELECT version();"))
        print(f"PostgreSQL Version: {ver.scalar()}")
        
        # DB name
        db = await session.execute(text("SELECT current_database();"))
        print(f"Current DB: {db.scalar()}")
        
        # User
        user = await session.execute(text("SELECT current_user;"))
        print(f"Current User: {user.scalar()}")
        
        # Extension
        ext_avail = await session.execute(text("SELECT * FROM pg_available_extensions WHERE name='vector';"))
        avail = ext_avail.fetchall()
        print(f"Available extensions matching 'vector': {avail}")
        
        ext_installed = await session.execute(text("SELECT * FROM pg_extension WHERE extname='vector';"))
        installed = ext_installed.fetchall()
        print(f"Installed extensions matching 'vector': {installed}")

if __name__ == "__main__":
    asyncio.run(verify_db())
