import logging
import uuid
import time
from typing import List
from database.repositories.document_chunk_repository import DocumentChunkRepository
from database.models.document_chunk import FailureReason, ChunkStatus
from app.services.embedding.base import AbstractEmbeddingProvider
from core.settings import Settings
import openai
import asyncio

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(
        self, 
        provider: AbstractEmbeddingProvider, 
        repository: DocumentChunkRepository,
        settings: Settings
    ):
        self.provider = provider
        self.repository = repository
        self.settings = settings
        self.capabilities = provider.capabilities()

    async def process_next_batch(self) -> int:
        """
        Acquires chunks and processes them. Returns the number of chunks processed.
        """
        # Determine strict batch size boundary
        batch_size = min(self.settings.embedding_max_batch_size, self.capabilities.max_batch_size)
        
        # 1. Acquire chunks safely via FOR UPDATE SKIP LOCKED
        chunks = await self.repository.acquire_chunks_for_processing(batch_size)
        if not chunks:
            return 0
            
        chunk_ids = [c.id for c in chunks]
        texts = [c.content for c in chunks]
        
        event_id = str(uuid.uuid4())
        
        logger.info({
            "event": "EmbeddingBatchStarted",
            "event_id": event_id,
            "chunk_count": len(chunks)
        })

        start_time = time.perf_counter()
        
        # 2. Budget Estimation pre-check
        # Very rough estimate assuming 1 token ≈ 4 characters if token_count isn't fully accurate, 
        # but chunks already have token_count populated by ChunkingService.
        total_tokens = sum(c.token_count for c in chunks if c.token_count)
        estimated_cost = total_tokens * (0.02 / 1_000_000) # $0.02 per 1M tokens (3-small)
        
        if estimated_cost > self.settings.embedding_max_cost_per_job:
            logger.error({
                "event": "EmbeddingFailed",
                "reason": "BUDGET_EXCEEDED",
                "estimated_cost": estimated_cost,
                "budget_cap": self.settings.embedding_max_cost_per_job
            })
            await self.repository.mark_failed(chunk_ids, FailureReason.BUDGET_EXCEEDED, to_status=ChunkStatus.FAILED, increment_retry=False)
            await self.repository.session.commit()
            return len(chunks)

        # 3. Provider Call
        try:
            # We bypass capturing the vectors because of pgvector block.
            vectors = await self.provider.embed_batch(texts)
            
            processing_ms = int((time.perf_counter() - start_time) * 1000)
            
            # 4. Mark Vector Pending (Vector Mocked)
            await self.repository.mark_vector_pending(
                chunk_ids=chunk_ids,
                provider="openai",
                model="text-embedding-3-small",
                dimension=1536,
                version="v1",
                processing_ms=processing_ms,
                token_usage=total_tokens,
                estimated_cost=f"{estimated_cost:.6f}"
            )
            await self.repository.session.commit()
            
            logger.info({
                "event": "EmbeddingBatchCompleted",
                "event_id": event_id,
                "provider": "openai",
                "model": "text-embedding-3-small",
                "batch_size": batch_size,
                "chunk_count": len(chunks),
                "token_usage": total_tokens,
                "processing_ms": processing_ms,
                "estimated_cost": f"{estimated_cost:.6f}",
                "retry_count": chunks[0].retry_count if chunks else 0,
                "success": True
            })
            
        except openai.RateLimitError:
            await self.repository.mark_failed(chunk_ids, FailureReason.RATE_LIMIT, to_status=ChunkStatus.RETRY_PENDING)
            await self.repository.session.commit()
        except openai.AuthenticationError:
            await self.repository.mark_failed(chunk_ids, FailureReason.INVALID_API_KEY, to_status=ChunkStatus.FAILED, increment_retry=False)
            await self.repository.session.commit()
        except Exception as e:
            await self.repository.mark_failed(chunk_ids, FailureReason.UNKNOWN, to_status=ChunkStatus.RETRY_PENDING)
            await self.repository.session.commit()
            logger.error({
                "event": "EmbeddingFailed",
                "error": str(e)
            })
            
        return len(chunks)
