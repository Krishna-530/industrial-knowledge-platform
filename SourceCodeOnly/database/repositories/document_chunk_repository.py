import logging
from typing import List, Optional, Any
from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.document_chunk import DocumentChunk, ChunkStatus, FailureReason
from sqlalchemy import func
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

class DocumentChunkRepository:
    """
    Repository for persisting DocumentChunks.
    Strictly follows the repository pattern and manages all embedding lifecycle status transitions.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_document_version(self, version_id: uuid.UUID) -> List[DocumentChunk]:
        result = await self.session.execute(
            select(DocumentChunk).where(DocumentChunk.document_version_id == version_id).order_by(DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count(DocumentChunk.id)))
        return result.scalar() or 0
        
    async def get_by_checksum(self, checksum: str) -> Optional[DocumentChunk]:
        result = await self.session.execute(
            select(DocumentChunk).where(DocumentChunk.checksum == checksum)
        )
        return result.scalars().first()

    async def save_chunks(self, chunks: List[DocumentChunk]) -> None:
        self.session.add_all(chunks)
        
    async def delete_by_document_version(self, version_id: uuid.UUID) -> int:
        result = await self.session.execute(
            delete(DocumentChunk).where(DocumentChunk.document_version_id == version_id)
        )
        return result.rowcount

    async def acquire_chunks_for_processing(self, batch_size: int) -> List[DocumentChunk]:
        """
        Acquires a batch of chunks safely using FOR UPDATE SKIP LOCKED.
        This explicitly prevents multiple workers from pulling the same chunks.
        """
        stmt = text("""
            UPDATE document_chunks
            SET status = 'PROCESSING'
            WHERE id IN (
                SELECT id 
                FROM document_chunks 
                WHERE status IN ('PENDING', 'RETRY_PENDING') 
                ORDER BY created_at ASC 
                LIMIT :batch_size 
                FOR UPDATE SKIP LOCKED
            )
            RETURNING *;
        """)
        
        # We need to map raw result rows back to DocumentChunk models,
        # or just return the IDs and do a select.
        # It's cleaner to return IDs and select them since we need the ORM objects.
        
        async with self.session.begin_nested():
            id_result = await self.session.execute(text("""
                UPDATE document_chunks
                SET status = 'PROCESSING'
                WHERE id IN (
                    SELECT id 
                    FROM document_chunks 
                    WHERE status IN ('PENDING', 'RETRY_PENDING') 
                    ORDER BY created_at ASC 
                    LIMIT :batch_size 
                    FOR UPDATE SKIP LOCKED
                )
                RETURNING id;
            """), {"batch_size": batch_size})
            
            acquired_ids = [row[0] for row in id_result.fetchall()]
            
            if not acquired_ids:
                return []
                
            result = await self.session.execute(
                select(DocumentChunk).where(DocumentChunk.id.in_(acquired_ids))
            )
            return list(result.scalars().all())

    async def mark_vector_pending(
        self, 
        chunk_ids: List[uuid.UUID], 
        provider: str, 
        model: str, 
        dimension: int,
        version: str,
        processing_ms: int,
        token_usage: int,
        estimated_cost: str,
        retry_count: int = 0
    ) -> None:
        if not chunk_ids:
            return
            
        await self.session.execute(text("""
            UPDATE document_chunks
            SET status = 'VECTOR_PENDING',
                embedding_provider = :provider,
                embedding_model = :model,
                embedding_dimension = :dimension,
                embedding_version = :version,
                embedded_at = :embedded_at,
                processing_ms = :processing_ms,
                token_usage = :token_usage,
                estimated_cost = :estimated_cost,
                retry_count = :retry_count
            WHERE id = ANY(:chunk_ids)
        """), {
            "chunk_ids": [str(cid) for cid in chunk_ids],
            "provider": provider,
            "model": model,
            "dimension": dimension,
            "version": version,
            "embedded_at": datetime.now(timezone.utc),
            "processing_ms": processing_ms,
            "token_usage": token_usage,
            "estimated_cost": estimated_cost,
            "retry_count": retry_count
        })

    async def mark_failed(
        self, 
        chunk_ids: List[uuid.UUID], 
        reason: FailureReason, 
        to_status: ChunkStatus = ChunkStatus.RETRY_PENDING,
        increment_retry: bool = True
    ) -> None:
        if not chunk_ids:
            return
            
        retry_inc = "retry_count + 1" if increment_retry else "retry_count"
        
        await self.session.execute(text(f"""
            UPDATE document_chunks
            SET status = :status,
                failure_reason = :reason,
                retry_count = {retry_inc}
            WHERE id = ANY(:chunk_ids)
        """), {
            "chunk_ids": [str(cid) for cid in chunk_ids],
            "status": to_status.value,
            "reason": reason.value
        })

    async def recover_stale_chunks(self, timeout_seconds: int, retry_limit: int) -> int:
        """
        Sweeps chunks that have been stuck in 'PROCESSING' for too long (due to worker crash).
        """
        result = await self.session.execute(text("""
            UPDATE document_chunks
            SET status = 'RETRY_PENDING',
                failure_reason = 'UNKNOWN'
            WHERE status = 'PROCESSING'
              AND extract(epoch from (now() - created_at)) > :timeout_seconds
              AND retry_count < :retry_limit
        """), {
            "timeout_seconds": timeout_seconds * 2,
            "retry_limit": retry_limit
        })
        return result.rowcount
