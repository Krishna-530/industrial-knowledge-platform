from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import get_db_session
from database.repositories.document import DocumentRepository, DocumentVersionRepository
from database.repositories.document_content_repository import DocumentContentRepository

def provide_document_repo(session: AsyncSession = Depends(get_db_session)) -> DocumentRepository:
    return DocumentRepository(session)

def provide_document_version_repo(session: AsyncSession = Depends(get_db_session)) -> DocumentVersionRepository:
    return DocumentVersionRepository(session)

def provide_content_repo(session: AsyncSession = Depends(get_db_session)) -> DocumentContentRepository:
    return DocumentContentRepository(session)
