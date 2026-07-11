import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.settings import Settings
from core.logging import setup_logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI application."""
    # Retrieve settings (they can be instantiated here directly or passed if needed)
    settings = Settings()
    
    # Initialize structured logging on startup
    setup_logging(level=settings.log_level, format_type=settings.log_format)
    
    logger.info(
        f"Starting up {settings.app_name} (v{settings.app_version})...",
        extra={"app_version": settings.app_version}
    )
    logger.info("Registering event subscriptions...")
    from core.event_bus import get_event_publisher
    from core.events.document_uploaded import DocumentUploaded
    from core.events.document_processed import DocumentProcessed
    from app.events.handlers import handle_document_uploaded, handle_document_processed
    
    publisher = get_event_publisher()
    publisher.subscribe(DocumentUploaded, handle_document_uploaded)
    publisher.subscribe(DocumentProcessed, handle_document_processed)
    
    logger.info("Recovering orphaned jobs...")
    from database.engine import async_session_maker
    from app.services.job_service import JobService
    
    async with async_session_maker() as session:
        job_service = JobService(session)
        await job_service.recover_orphaned_jobs(timeout_minutes=settings.worker_orphan_timeout_minutes)
        
    logger.info("Starting WorkerManager...")
    from api.v1.dependencies.workers import provide_worker_manager
    
    worker_manager = provide_worker_manager()
    await worker_manager.start_all()
    
    yield
    
    logger.info("Stopping WorkerManager...")
    await worker_manager.stop_all()
    
    logger.info("Shutting down database engine...")
    from database.engine import engine
    await engine.dispose()
    logger.info("Shutting down...")
