import asyncio
from sqlalchemy import text
from database.engine import async_session_factory

async def drop_enum():
    async with async_session_factory() as session:
        await session.execute(text("DROP TYPE IF EXISTS chunkstatus CASCADE;"))
        await session.commit()
        print("Dropped chunkstatus enum")

if __name__ == "__main__":
    asyncio.run(drop_enum())
