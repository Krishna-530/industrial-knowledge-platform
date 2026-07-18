import asyncio
import logging
from core.settings import Settings
from database.session import async_session_factory
from database.repositories.document_chunk_repository import DocumentChunkRepository
from app.services.embedding.factory import ProviderFactory
from app.services.embedding.service import EmbeddingService

logger = logging.getLogger(__name__)

async def run_embedding_worker():
    settings = Settings()
    
    # Feature flag kill switch
    if not settings.enable_embeddings:
        logger.info({"event": "WorkerDisabled", "reason": "ENABLE_EMBEDDINGS is false"})
        return
        
    provider = ProviderFactory.get_provider(settings)
    
    # Health Check Endpoint Guard
    if not await provider.health_check():
        logger.error({"event": "WorkerAborted", "reason": "Provider health check failed"})
        return

    logger.info({"event": "WorkerStarted", "worker_id": settings.worker_id})
    
    concurrency_sem = asyncio.Semaphore(settings.embedding_max_concurrency)

    while True:
        try:
            async with async_session_factory() as session:
                repo = DocumentChunkRepository(session)
                service = EmbeddingService(provider, repo, settings)
                
                # Recover stale chunks periodically (simplification for the loop)
                await repo.recover_stale_chunks(
                    timeout_seconds=settings.embedding_timeout_seconds, 
                    retry_limit=settings.embedding_retry_limit
                )
                await session.commit()
                
                # We acquire and process batches
                async with concurrency_sem:
                    processed = await service.process_next_batch()
                    
            if processed == 0:
                await asyncio.sleep(settings.worker_poll_interval)
            else:
                # Yield to event loop gently
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            logger.info({"event": "WorkerCancelled"})
            break
        except Exception as e:
            logger.error({"event": "WorkerError", "error": str(e)})
            await asyncio.sleep(settings.worker_poll_interval)

if __name__ == "__main__":
    asyncio.run(run_embedding_worker())
