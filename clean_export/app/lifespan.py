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
    
    # Telemetry subscriptions
    from app.events.telemetry_subscriber import telemetry_subscriber
    from core.events.telemetry import (
        SearchCompletedEvent, DocumentUploadedEvent, JobCompletedEvent,
        UserLoggedInEvent, DocumentViewedEvent, DashboardViewedEvent
    )
    publisher.subscribe(SearchCompletedEvent, telemetry_subscriber.handle_search_completed)
    publisher.subscribe(DocumentUploadedEvent, telemetry_subscriber.handle_telemetry_event)
    publisher.subscribe(JobCompletedEvent, telemetry_subscriber.handle_telemetry_event)
    publisher.subscribe(UserLoggedInEvent, telemetry_subscriber.handle_telemetry_event)
    publisher.subscribe(DocumentViewedEvent, telemetry_subscriber.handle_telemetry_event)
    publisher.subscribe(DashboardViewedEvent, telemetry_subscriber.handle_telemetry_event)
    
    logger.info("Recovering orphaned jobs...")
    from database.engine import async_session_factory
    from app.services.job_service import JobService
    
    async with async_session_factory() as session:
        job_service = JobService(session)
        await job_service.recover_orphaned_jobs(timeout_minutes=settings.worker_orphan_timeout_minutes)
        
    logger.info("Starting WorkerManager...")
    from api.v1.dependencies.workers import provide_worker_manager
    
    worker_manager = provide_worker_manager()
    await worker_manager.start_all()
    
    # Initialize Neo4j Driver if enabled
    if settings.enable_knowledge_graph:
        logger.info("Initializing Neo4j Graph Database...")
        from database.neo4j_driver import Neo4jDriverManager
        driver_manager = Neo4jDriverManager.get_instance(settings)
        await driver_manager.connect()
    
    yield
    
    logger.info("Stopping WorkerManager...")
    await worker_manager.stop_all()
    
    logger.info("Shutting down database engine...")
    from database.engine import engine
    await engine.dispose()
    
    if settings.enable_knowledge_graph:
        from database.neo4j_driver import Neo4jDriverManager
        driver_manager = Neo4jDriverManager.get_instance(settings)
        await driver_manager.close()
        
    logger.info("Shutting down...")
