import logging
from database.engine import async_session_factory
from database.models.search_log import SearchLog
from database.models.telemetry_event import TelemetryEvent
from core.events.telemetry import (
    SearchCompletedEvent, 
    DocumentUploadedEvent, 
    JobCompletedEvent, 
    UserLoggedInEvent,
    DocumentViewedEvent,
    DashboardViewedEvent,
    BaseTelemetryEvent
)

logger = logging.getLogger(__name__)

class TelemetrySubscriber:
    """
    Subscribes to all telemetry events and safely persists them to the database.
    Idempotent and swallows exceptions so the main thread never fails.
    """
    async def handle_search_completed(self, event: SearchCompletedEvent):
        await self._safe_execute(self._persist_search, event)

    async def handle_telemetry_event(self, event: BaseTelemetryEvent):
        await self._safe_execute(self._persist_platform_event, event)

    async def _safe_execute(self, func, event: BaseTelemetryEvent):
        try:
            async with async_session_factory() as session:
                await func(session, event)
                await session.commit()
        except Exception as e:
            # Swallow the exception to ensure best-effort delivery
            logger.error({
                "event": "telemetry_write_failed",
                "telemetry_event_id": str(event.event_id),
                "request_id": event.request_id,
                "correlation_id": event.correlation_id,
                "error": str(e)
            })

    async def _persist_search(self, session, event: SearchCompletedEvent):
        log = SearchLog(
            event_id=event.event_id,
            request_id=event.request_id,
            correlation_id=event.correlation_id,
            user_id=event.user_id,
            query=event.query,
            retrieval_strategy=event.retrieval_strategy,
            execution_time_ms=event.execution_time_ms,
            result_count=event.result_count,
            success=event.success
        )
        session.add(log)

    async def _persist_platform_event(self, session, event: BaseTelemetryEvent):
        event_type = event.__class__.__name__
        
        # Base attributes
        log = TelemetryEvent(
            event_id=event.event_id,
            request_id=event.request_id,
            correlation_id=event.correlation_id,
            event_type=event_type,
            payload=event.model_dump(mode="json", exclude={"event_id", "request_id", "correlation_id", "timestamp"})
        )

        # Extract common indexed fields if they exist
        if hasattr(event, "user_id"):
            log.user_id = event.user_id
        if hasattr(event, "document_id"):
            log.document_id = event.document_id

        session.add(log)

telemetry_subscriber = TelemetrySubscriber()
