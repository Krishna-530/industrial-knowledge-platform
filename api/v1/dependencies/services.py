from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import get_db_session

from core.settings import Settings
from core.event_bus import get_event_publisher
from core.event_bus.publisher import EventPublisher

from app.storage.local import LocalStorageProvider
from app.storage.service import StorageService

from database.repositories.document import DocumentRepository
from database.repositories.version import VersionRepository
from database.repositories.document_content_repository import DocumentContentRepository

from app.services.document_service import DocumentService
from app.services.document_content_service import DocumentContentService
from app.processing.service import ProcessingService

from app.services.knowledge_fact_service import KnowledgeFactService
from app.services.knowledge_intelligence_service import KnowledgeIntelligenceService
from app.services.knowledge_analytics_service import KnowledgeAnalyticsService
from app.services.dashboard_service import DashboardService
from database.repositories.extracted_fact_repository import ExtractedFactRepository
from database.repositories.intelligence_finding_repository import IntelligenceFindingRepository

from api.v1.dependencies.settings import provide_settings
from api.v1.dependencies.repositories import provide_document_repo, provide_document_version_repo, provide_content_repo
from app.services.graph_service import KnowledgeGraphService
from app.services.graph_query_service import GraphQueryService
from database.neo4j_driver import Neo4jDriverManager
from database.repositories.graph_repository import Neo4jGraphRepository
from database.repositories.graph_readonly_repository import ReadOnlyGraphRepository
from app.services.document_explorer_service import DocumentExplorerService
from app.services.dashboard_service import DashboardService
from database.repositories.document_chunk_repository import DocumentChunkRepository
from database.repositories.entity_repository import EntityRepository
from database.repositories.relationship_repository import RelationshipRepository
from database.repositories.job_repository import JobRepository

def provide_graph_service(settings: Settings = Depends(provide_settings)) -> KnowledgeGraphService:
    driver_manager = Neo4jDriverManager.get_instance(settings)
    repo = Neo4jGraphRepository(driver_manager.driver) if driver_manager._driver else None
    return KnowledgeGraphService(graph_repository=repo)

def provide_graph_query_service(settings: Settings = Depends(provide_settings)) -> GraphQueryService:
    driver_manager = Neo4jDriverManager.get_instance(settings)
    repo = ReadOnlyGraphRepository(driver_manager.driver) if driver_manager._driver else None
    return GraphQueryService(readonly_repo=repo)

def provide_storage_service(settings: Settings = Depends(provide_settings)) -> StorageService:
    provider = LocalStorageProvider(base_directory=settings.upload_directory)
    return StorageService(provider=provider)

def provide_event_publisher() -> EventPublisher:
    return get_event_publisher()



def provide_processing_service() -> ProcessingService:
    return ProcessingService()

def provide_knowledge_intelligence_service(
    session: AsyncSession = Depends(get_db_session)
) -> KnowledgeIntelligenceService:
    finding_repo = IntelligenceFindingRepository(session)
    return KnowledgeIntelligenceService(session=session, finding_repo=finding_repo)

def provide_knowledge_fact_service(
    session: AsyncSession = Depends(get_db_session),
    intelligence_service: KnowledgeIntelligenceService = Depends(provide_knowledge_intelligence_service)
) -> KnowledgeFactService:
    fact_repo = ExtractedFactRepository(session)
    return KnowledgeFactService(session=session, fact_repo=fact_repo, intelligence_service=intelligence_service)

def provide_content_service(
    session: AsyncSession = Depends(get_db_session),
    repo: DocumentContentRepository = Depends(provide_content_repo)
) -> DocumentContentService:
    return DocumentContentService(session, repo)

def provide_document_service(
    session: AsyncSession = Depends(get_db_session),
    doc_repo: DocumentRepository = Depends(provide_document_repo),
    version_repo: VersionRepository = Depends(provide_document_version_repo),
    knowledge_fact_service: KnowledgeFactService = Depends(provide_knowledge_fact_service),
    storage_service = Depends(provide_storage_service)
) -> DocumentService:
    return DocumentService(
        session=session,
        storage_service=storage_service,
        knowledge_fact_service=knowledge_fact_service
    )

def provide_knowledge_analytics_service(
    session: AsyncSession = Depends(get_db_session)
) -> KnowledgeAnalyticsService:
    from database.repositories.intelligence_finding_repository import IntelligenceFindingRepository
    finding_repo = IntelligenceFindingRepository(session)
    fact_repo = ExtractedFactRepository(session)
    return KnowledgeAnalyticsService(session, fact_repo, finding_repo)

def provide_dashboard_service(
    session: AsyncSession = Depends(get_db_session),
    analytics_service: KnowledgeAnalyticsService = Depends(provide_knowledge_analytics_service),
    document_service: DocumentService = Depends(provide_document_service),
    graph_service: GraphQueryService = Depends(provide_graph_query_service),
    document_repo: DocumentRepository = Depends(provide_document_repo)
) -> DashboardService:
    from database.repositories.document_chunk_repository import DocumentChunkRepository
    from database.repositories.entity_repository import EntityRepository
    from database.repositories.relationship_repository import RelationshipRepository
    from database.repositories.job_repository import JobRepository
    
    return DashboardService(
        analytics_service=analytics_service, 
        document_service=document_service,
        graph_service=graph_service,
        document_repo=document_repo,
        chunk_repo=DocumentChunkRepository(session),
        entity_repo=EntityRepository(session),
        relationship_repo=RelationshipRepository(session),
        job_repo=JobRepository(session)
    )

def provide_infrastructure_health_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(provide_settings)
):
    from app.services.infrastructure_health_service import InfrastructureHealthService
    from app.llm.providers.groq_provider import GroqProvider
    from app.llm.providers.groq_config import GroqConfig
    from app.services.embedding.openai_provider import OpenAIEmbeddingProvider
    
    groq_config = GroqConfig(api_key=settings.groq_api_key or "NO_KEY")
    llm_provider = GroqProvider(groq_config)
    embedding_provider = OpenAIEmbeddingProvider(api_key=settings.openai_api_key or "NO_KEY")
    
    return InfrastructureHealthService(session, llm_provider, embedding_provider, settings)

def provide_dashboard_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(provide_settings),
) -> DashboardService:
    from app.services.knowledge_analytics_service import KnowledgeAnalyticsService
    from database.repositories.extracted_fact_repository import ExtractedFactRepository
    from database.repositories.intelligence_finding_repository import IntelligenceFindingRepository
    from app.services.document_service import DocumentService as _DocumentService

    fact_repo = ExtractedFactRepository(session)
    finding_repo = IntelligenceFindingRepository(session)
    analytics_service = KnowledgeAnalyticsService(session, fact_repo, finding_repo)
    document_service = _DocumentService(session)
    graph_query_service = provide_graph_query_service(settings)
    document_repo = DocumentRepository(session)
    chunk_repo = DocumentChunkRepository(session)
    entity_repo = EntityRepository(session)
    relationship_repo = RelationshipRepository(session)
    job_repo = JobRepository(session)

    return DashboardService(
        analytics_service=analytics_service,
        document_service=document_service,
        graph_service=graph_query_service,
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        entity_repo=entity_repo,
        relationship_repo=relationship_repo,
        job_repo=job_repo,
    )


def provide_admin_service(
    session: AsyncSession = Depends(get_db_session),
    dashboard_service: DashboardService = Depends(provide_dashboard_service),
    document_service: DocumentService = Depends(provide_document_service),
    infra_health = Depends(provide_infrastructure_health_service)
):
    from app.services.admin_service import AdminService
    from app.services.user_service import UserService
    from app.services.job_service import JobService
    from database.repositories.version import VersionRepository
    
    return AdminService(
        dashboard_service=dashboard_service,
        user_service=UserService(session),
        document_service=document_service,
        job_service=JobService(session),
        version_repo=VersionRepository(session),
        infra_health=infra_health
    )


def provide_document_explorer_service(
    settings: Settings = Depends(provide_settings),
) -> DocumentExplorerService:
    """Provides DocumentExplorerService backed by Neo4j read repo.
    Returns a service with a None repo when knowledge graph is disabled;
    the service methods guard against None and return empty lists.
    """
    if not settings.enable_knowledge_graph:
        return DocumentExplorerService(readonly_repo=None)  # type: ignore[arg-type]
    driver_manager = Neo4jDriverManager.get_instance(settings)
    repo = ReadOnlyGraphRepository(driver_manager.driver) if driver_manager._driver else None
    return DocumentExplorerService(readonly_repo=repo)  # type: ignore[arg-type]
