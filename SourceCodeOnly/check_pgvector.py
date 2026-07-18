import asyncio
from sqlalchemy import text
from database.engine import async_session_factory

async def check_pgvector():
    async with async_session_factory() as session:
        # Check if the extension is available on the system
        result = await session.execute(text("SELECT name FROM pg_available_extensions;"))
        extensions = result.fetchall()
        print(f"Available extensions ({len(extensions)}):")
        for ext in extensions:
            if "vector" in ext.name:
                print(f"Found vector related: {ext.name}")

if __name__ == "__main__":
    asyncio.run(check_pgvector())
