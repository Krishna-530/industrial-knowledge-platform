import asyncio
from database.engine import async_session_factory
from database.models.job import Job
from sqlalchemy import select

async def run():
    async with async_session_factory() as s:
        res = await s.execute(select(Job).order_by(Job.created_at.desc()).limit(1))
        job = res.scalar()
        if job:
            print("ID:", job.id)
            print("Status:", job.status)
            print("Type:", job.job_type)
            print("DeadLetter:", job.is_dead_letter)
            print("NextRetry:", job.next_retry_at)
            print("Attempts:", job.attempts)
        else:
            print("No job")

asyncio.run(run())
