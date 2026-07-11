from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import get_db_session

from app.search.interfaces import AbstractSearchProvider
from app.search.providers.postgres import PostgresSearchProvider
from app.search.search_service import SearchService
from app.search.indexing_service import IndexingService
from app.workflows.search_workflow import SearchWorkflow
from app.workflows.indexing_workflow import IndexingWorkflow
from database.repositories.document_content_repository import DocumentContentRepository
from api.v1.dependencies.repositories import provide_content_repo

def provide_search_provider(session: AsyncSession = Depends(get_db_session)) -> AbstractSearchProvider:
    return PostgresSearchProvider(session)

def provide_search_service(provider: AbstractSearchProvider = Depends(provide_search_provider)) -> SearchService:
    return SearchService(provider)

def provide_indexing_service(
    session: AsyncSession = Depends(get_db_session),
    provider: AbstractSearchProvider = Depends(provide_search_provider),
    content_repo: DocumentContentRepository = Depends(provide_content_repo)
) -> IndexingService:
    return IndexingService(session, provider, content_repo)

def provide_search_workflow(search_service: SearchService = Depends(provide_search_service)) -> SearchWorkflow:
    return SearchWorkflow(search_service)

def provide_indexing_workflow(indexing_service: IndexingService = Depends(provide_indexing_service)) -> IndexingWorkflow:
    return IndexingWorkflow(indexing_service)
