from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import get_db_session
from database.repositories.extracted_fact_repository import ExtractedFactRepository
from database.repositories.intelligence_finding_repository import IntelligenceFindingRepository
from app.services.knowledge_analytics_service import KnowledgeAnalyticsService

def provide_analytics_service(
    session: AsyncSession = Depends(get_db_session)
) -> KnowledgeAnalyticsService:
    fact_repo = ExtractedFactRepository(session)
    finding_repo = IntelligenceFindingRepository(session)
    return KnowledgeAnalyticsService(session=session, fact_repo=fact_repo, finding_repo=finding_repo)
