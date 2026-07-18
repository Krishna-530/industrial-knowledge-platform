import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.analytics_repository import AnalyticsRepository
from api.v1.schemas.enterprise_analytics import EnterpriseAnalyticsResponse

logger = logging.getLogger(__name__)

class EnterpriseAnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.analytics_repo = AnalyticsRepository(session)

    async def get_enterprise_analytics(
        self, 
        start_date: datetime = None, 
        end_date: datetime = None
    ) -> EnterpriseAnalyticsResponse:
        
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        logger.info({"event": "fetch_enterprise_analytics", "start_date": start_date.isoformat(), "end_date": end_date.isoformat()})
        
        return await self.analytics_repo.get_enterprise_analytics(start_date, end_date)
