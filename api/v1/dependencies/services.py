from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import get_db_session

from core.settings import Settings
from core.event_bus import get_event_publisher
from core.event_bus.publisher import EventPublisher

from app.storage.local import LocalStorageProvider
from app.storage.service import StorageService

from database.repositories.document import DocumentRepository, DocumentVersionRepository
from database.repositories.document_content_repository import DocumentContentRepository

from app.services.document_service import DocumentService
from app.services.document_content_service import DocumentContentService
from app.processing.service import ProcessingService

from api.v1.dependencies.settings import provide_settings
from api.v1.dependencies.repositories import provide_document_repo, provide_document_version_repo, provide_content_repo

def provide_storage_service(settings: Settings = Depends(provide_settings)) -> StorageService:
    provider = LocalStorageProvider(base_path=settings.storage_base_path)
    return StorageService(provider=provider)

def provide_event_publisher() -> EventPublisher:
    return get_event_publisher()

def provide_document_service(
    session: AsyncSession = Depends(get_db_session),
    doc_repo: DocumentRepository = Depends(provide_document_repo),
    version_repo: DocumentVersionRepository = Depends(provide_document_version_repo)
) -> DocumentService:
    return DocumentService(session)

def provide_content_service(
    session: AsyncSession = Depends(get_db_session),
    repo: DocumentContentRepository = Depends(provide_content_repo)
) -> DocumentContentService:
    return DocumentContentService(session, repo)

def provide_processing_service() -> ProcessingService:
    return ProcessingService()
