from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import get_db_session

from app.search.search_service import SearchService
from api.v1.dependencies.search import provide_search_service

from app.services.authorization_service import AuthorizationService
from app.retrieval.interfaces import AbstractRetrievalStrategy, AbstractRanker
from app.retrieval.strategies.keyword_strategy import KeywordRetrievalStrategy
from app.retrieval.rankers.standard_ranker import StandardRanker
from app.retrieval.knowledge_assembler import KnowledgeAssembler
from app.retrieval.retrieval_service import RetrievalService
from app.workflows.retrieval_workflow import RetrievalWorkflow

def provide_authorization_service() -> AuthorizationService:
    return AuthorizationService()

def provide_retrieval_strategy(search_service: SearchService = Depends(provide_search_service)) -> AbstractRetrievalStrategy:
    return KeywordRetrievalStrategy(search_service)

def provide_retrieval_ranker() -> AbstractRanker:
    return StandardRanker()

def provide_knowledge_assembler(session: AsyncSession = Depends(get_db_session)) -> KnowledgeAssembler:
    return KnowledgeAssembler(session)

def provide_retrieval_service(
    strategy: AbstractRetrievalStrategy = Depends(provide_retrieval_strategy),
    ranker: AbstractRanker = Depends(provide_retrieval_ranker),
    assembler: KnowledgeAssembler = Depends(provide_knowledge_assembler),
    authorization_service: AuthorizationService = Depends(provide_authorization_service)
) -> RetrievalService:
    return RetrievalService(strategy, ranker, assembler, authorization_service)

def provide_retrieval_workflow(
    retrieval_service: RetrievalService = Depends(provide_retrieval_service)
) -> RetrievalWorkflow:
    return RetrievalWorkflow(retrieval_service)
