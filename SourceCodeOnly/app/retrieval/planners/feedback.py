import logging
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

class PlannerFeedbackEvent(BaseModel):
    query: str
    decision: str
    latency_ms: int
    cache_hit: bool
    fallback_triggered: bool
    success: bool
    user_rating: Optional[int] = None

class PlannerFeedbackService:
    """
    Captures telemetry and outcome data for Retrieval Planner decisions.
    Feeds back into future prompt optimization or model fine-tuning.
    """
    
    @staticmethod
    def record_event(event: PlannerFeedbackEvent) -> None:
        """
        Records the event. In production, this would emit to a telemetry stream or DB.
        """
        logger.info(
            f"Planner Feedback | Query: '{event.query}' | Decision: {event.decision} | "
            f"Latency: {event.latency_ms}ms | Success: {event.success} | Fallback: {event.fallback_triggered}"
        )
        # TODO: Persist to 'planner_telemetry' table.
