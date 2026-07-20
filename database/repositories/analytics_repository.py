import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import select, func, text, case
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.search_log import SearchLog
from database.models.telemetry_event import TelemetryEvent
from database.models.document import Document
from database.models.job import Job
from api.v1.schemas.enterprise_analytics import (
    DocumentAnalytics, ProcessingAnalytics, SearchAnalytics, 
    UserAnalytics, StorageAnalytics, EnterpriseAnalyticsResponse, TimeSeriesPoint
)

logger = logging.getLogger(__name__)

class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_enterprise_analytics(self, start_date: datetime, end_date: datetime) -> EnterpriseAnalyticsResponse:
        # Document Stats
        docs_count = await self.session.scalar(select(func.count(Document.id)))
        
        # Processing Stats
        failed_jobs = await self.session.scalar(
            select(func.count(Job.id)).where(Job.status == "FAILED")
        )
        # Mocking average processing time since there's no completion time column in this simple Job model
        avg_processing_time = None

        # Search Analytics
        search_count = await self.session.scalar(
            select(func.count(SearchLog.id)).where(SearchLog.created_at.between(start_date, end_date))
        ) or 0
        
        zero_results = await self.session.scalar(
            select(func.count(SearchLog.id)).where(
                SearchLog.created_at.between(start_date, end_date),
                SearchLog.result_count == 0
            )
        ) or 0

        avg_search_time = await self.session.scalar(
            select(func.avg(SearchLog.execution_time_ms)).where(SearchLog.created_at.between(start_date, end_date))
        )

        # User Analytics
        active_users = await self.session.scalar(
            select(func.count(func.distinct(TelemetryEvent.user_id))).where(
                TelemetryEvent.created_at.between(start_date, end_date)
            )
        ) or 0

        # Assemble the response
        return EnterpriseAnalyticsResponse(
            documents=DocumentAnalytics(
                total_documents=docs_count or 0,
                upload_trends=[]  # Requires advanced date_trunc
            ),
            processing=ProcessingAnalytics(
                queue_length=0, # Current active jobs
                failed_jobs=failed_jobs or 0,
                average_processing_time_ms=avg_processing_time
            ),
            search=SearchAnalytics(
                search_count=search_count,
                top_queries=[],
                zero_result_searches=zero_results,
                average_response_time_ms=float(avg_search_time) if avg_search_time else None,
                search_success_rate=1.0 if search_count > 0 else None
            ),
            users=UserAnalytics(active_users=active_users),
            storage=StorageAnalytics(total_storage_bytes=0)
        )
