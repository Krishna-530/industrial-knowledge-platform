import asyncio
from database.engine import async_session_factory
from database.models.job import Job
from sqlalchemy import select

async def run():
    async with async_session_factory() as s:
        res = await s.execute(select(Job).where(Job.id == 'a7dc3e0e-d007-46f7-94df-abf6eb6b641e'))
        job = res.scalar()
        print(job.error_message)

asyncio.run(run())
