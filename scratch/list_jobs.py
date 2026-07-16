import asyncio
from database.engine import async_session_factory
from database.models.job import Job
from sqlalchemy import select

async def run():
    async with async_session_factory() as s:
        res = await s.execute(select(Job).order_by(Job.created_at.desc()).limit(5))
        jobs = res.scalars().all()
        for job in jobs:
            print("ID:", job.id, "Status:", job.status.value, "Type:", job.job_type, "Attempts:", job.attempts, "DeadLetter:", job.is_dead_letter, "Error:", str(job.error_message)[:50])

asyncio.run(run())
