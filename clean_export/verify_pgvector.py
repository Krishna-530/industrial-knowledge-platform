import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from core.settings import Settings

async def main():
    settings = Settings()
    engine = create_async_engine(settings.database_url)
    try:
        async with engine.connect() as conn:
            # 1. DB version
            res = await conn.execute(text("SELECT version();"))
            print(f"DB Version: {res.scalar()}")
            
            # 2. Check extension
            res = await conn.execute(text("SELECT * FROM pg_available_extensions WHERE name = 'vector';"))
            row = res.first()
            if row:
                print(f"pgvector available: {row}")
            else:
                print("pgvector NOT available in pg_available_extensions")
                
            # 3. Try to create extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                print("CREATE EXTENSION vector succeeded")
            except Exception as e:
                print(f"CREATE EXTENSION vector failed: {e}")
                
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
