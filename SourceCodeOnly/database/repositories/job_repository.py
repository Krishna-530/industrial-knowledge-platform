from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from database.models.job import Job
from core.enums.job_status import JobStatus
from datetime import datetime, timezone

class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, job_type: str, payload: dict) -> Job:
        job = Job(job_type=job_type, payload=payload, status=JobStatus.QUEUED)
        self.session.add(job)
        await self.session.flush()
        return job

    async def get_by_id(self, job_id: UUID) -> Optional[Job]:
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        return result.scalars().first()

    async def get_queue_metrics(self) -> dict:
        stmt = select(Job.status, func.count(Job.id)).group_by(Job.status)
        result = await self.session.execute(stmt)
        metrics = {status.value: count for status, count in result.all()}
        metrics["TOTAL"] = sum(metrics.values())
        return metrics

    async def get_recent_jobs(self, limit: int = 10) -> List[Job]:
        stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def dequeue(self, supported_types: List[str]) -> Optional[Job]:
        # Lock one QUEUED job where next_retry_at is <= now or null
        now = datetime.now(timezone.utc)
        
        stmt = (
            select(Job)
            .where(
                and_(
                    Job.status == JobStatus.QUEUED,
                    Job.job_type.in_(supported_types),
                    (Job.next_retry_at <= now) | (Job.next_retry_at.is_(None)),
                    Job.is_dead_letter == False
                )
            )
            .order_by(Job.next_retry_at.asc().nulls_first(), Job.created_at.asc())
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        
        result = await self.session.execute(stmt)
        job = result.scalars().first()
        return job

    async def update(self, job: Job, **fields) -> Job:
        for key, value in fields.items():
            setattr(job, key, value)
        await self.session.flush()
        return job

    async def count_jobs(self, status: Optional[str] = None, job_type: Optional[str] = None, search: Optional[str] = None) -> int:
        from sqlalchemy import String, cast, or_
        stmt = select(func.count(Job.id))
        
        conditions = []
        if status:
            conditions.append(Job.status == JobStatus(status))
        if job_type:
            conditions.append(Job.job_type == job_type)
        if search:
            conditions.append(
                or_(
                    cast(Job.id, String).ilike(f"%{search}%"),
                    Job.error_message.ilike(f"%{search}%")
                )
            )
            
        if conditions:
            stmt = stmt.where(and_(*conditions))
            
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def list_jobs(self, limit: int = 50, offset: int = 0, status: Optional[str] = None, job_type: Optional[str] = None, search: Optional[str] = None) -> List[Job]:
        from sqlalchemy import String, cast, or_
        stmt = select(Job)
        
        conditions = []
        if status:
            conditions.append(Job.status == JobStatus(status))
        if job_type:
            conditions.append(Job.job_type == job_type)
        if search:
            conditions.append(
                or_(
                    cast(Job.id, String).ilike(f"%{search}%"),
                    Job.error_message.ilike(f"%{search}%")
                )
            )
            
        if conditions:
            stmt = stmt.where(and_(*conditions))
            
        stmt = stmt.order_by(Job.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
