import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.job_repository import JobRepository
from database.models.job import Job
from core.enums.job_status import JobStatus

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = JobRepository(session)

    async def enqueue(self, job_type: str, payload: Dict[str, Any], max_attempts: int = 3) -> Job:
        try:
            job = await self.repo.create(job_type, payload)
            job.max_attempts = max_attempts
            await self.session.commit()
            logger.info({"event": "job_enqueued", "job_id": str(job.id), "job_type": job_type})
            return job
        except Exception as e:
            await self.session.rollback()
            logger.error({"event": "job_enqueue_failed", "job_type": job_type, "error": str(e)})
            raise

    async def dequeue(self, supported_types: List[str], worker_id: str = "unknown") -> Optional[Job]:
        try:
            job = await self.repo.dequeue(supported_types)
            if job:
                job.status = JobStatus.PROCESSING
                job.started_at = datetime.now(timezone.utc)
                job.attempts += 1
                job.last_attempt_at = datetime.now(timezone.utc)
                await self.session.commit()
                # Emitting metrics
                queue_wait_ms = int((job.started_at - job.created_at).total_seconds() * 1000)
                logger.info({"event": "job_dequeued", "job_id": str(job.id), "job_type": job.job_type, "queue_wait_ms": queue_wait_ms, "attempt": job.attempts, "worker_id": worker_id})
            return job
        except Exception as e:
            await self.session.rollback()
            logger.error({"event": "job_dequeue_failed", "error": str(e), "worker_id": worker_id})
            raise

    async def mark_completed(self, job_id: UUID, worker_id: str = "unknown") -> None:
        try:
            job = await self.repo.get_by_id(job_id)
            if job:
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now(timezone.utc)
                await self.session.commit()
                processing_duration_ms = int((job.completed_at - job.started_at).total_seconds() * 1000)
                total_duration_ms = int((job.completed_at - job.created_at).total_seconds() * 1000)
                document_version_id = job.payload.get("version_id")
                
                logger.info({
                    "event": "job_completed",
                    "job_id": str(job_id),
                    "document_version_id": document_version_id,
                    "worker_id": worker_id,
                    "attempt": job.attempts,
                    "processing_duration_ms": processing_duration_ms,
                    "total_duration_ms": total_duration_ms,
                    "retry_count": max(0, job.attempts - 1),
                    "final_status": "COMPLETED"
                })
        except Exception as e:
            await self.session.rollback()
            logger.error({"event": "job_mark_completed_failed", "job_id": str(job_id), "error": str(e), "worker_id": worker_id})
            raise

    async def mark_failed(self, job_id: UUID, error_message: str, worker_id: str = "unknown", backoff_multiplier: int = 10) -> None:
        try:
            job = await self.repo.get_by_id(job_id)
            if job:
                now = datetime.now(timezone.utc)
                job.failed_at = now
                job.error_message = error_message
                
                if job.attempts >= job.max_attempts:
                    job.status = JobStatus.FAILED
                    job.is_dead_letter = True
                else:
                    job.status = JobStatus.QUEUED
                    backoff_seconds = (2 ** job.attempts) * backoff_multiplier
                    job.next_retry_at = now + timedelta(seconds=backoff_seconds)
                
                await self.session.commit()
                
                processing_duration_ms = int((now - job.started_at).total_seconds() * 1000) if job.started_at else 0
                total_duration_ms = int((now - job.created_at).total_seconds() * 1000)
                document_version_id = job.payload.get("version_id")
                
                logger.info({
                    "event": "job_failed",
                    "job_id": str(job_id),
                    "document_version_id": document_version_id,
                    "worker_id": worker_id,
                    "attempt": job.attempts,
                    "processing_duration_ms": processing_duration_ms,
                    "total_duration_ms": total_duration_ms,
                    "retry_count": max(0, job.attempts - 1),
                    "final_status": job.status.value,
                    "is_dead_letter": job.is_dead_letter,
                    "error": error_message
                })
        except Exception as e:
            await self.session.rollback()
            logger.error({"event": "job_mark_failed_error", "job_id": str(job_id), "error": str(e), "worker_id": worker_id})
            raise

    async def recover_orphaned_jobs(self, timeout_minutes: int) -> None:
        try:
            from sqlalchemy import select
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
            
            stmt = select(Job).where(
                Job.status == JobStatus.PROCESSING,
                Job.last_attempt_at < cutoff_time
            )
            result = await self.session.execute(stmt)
            orphaned_jobs = result.scalars().all()
            
            recovered_count = 0
            dead_lettered_count = 0
            
            for job in orphaned_jobs:
                # We already incremented attempts during dequeue. 
                # If a job is orphaned, it crashed during processing, meaning that attempt failed.
                # So the current attempt count accurately reflects the crashed attempt.
                
                if job.attempts >= job.max_attempts:
                    job.status = JobStatus.FAILED
                    job.is_dead_letter = True
                    job.error_message = f"Orphaned job recovered and dead-lettered after {job.attempts} attempts"
                    dead_lettered_count += 1
                else:
                    job.status = JobStatus.QUEUED
                    job.error_message = "Recovered orphaned job on startup"
                    job.next_retry_at = datetime.now(timezone.utc)
                    recovered_count += 1
                    
            if orphaned_jobs:
                await self.session.commit()
                logger.warning({
                    "event": "orphaned_jobs_recovered",
                    "recovered_to_queued": recovered_count,
                    "dead_lettered": dead_lettered_count,
                    "total_orphans": len(orphaned_jobs)
                })
        except Exception as e:
            await self.session.rollback()
            logger.error({"event": "orphaned_job_recovery_failed", "error": str(e)})
            raise
