import logging
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.cost import ExtractionCostLog
import uuid

logger = logging.getLogger(__name__)

class CostTracker:
    """
    Governs LLM budget by tracking extraction costs per job.
    In a fully distributed system, this would use Redis to enforce global monthly limits.
    """
    def __init__(self, session: AsyncSession, max_cost_per_job: float = 5.00):
        self.session = session
        self.max_cost_per_job = max_cost_per_job

    async def log_cost(self, job_id: uuid.UUID, metadata: dict, extraction_type: str = "ENTITY") -> None:
        """
        Calculates and logs the estimated cost of an extraction.
        """
        # Very rough approximation of cost calculation. 
        # In reality, this requires a matrix of Provider/Model pricing.
        prompt_tokens = metadata.get("prompt_tokens", 0)
        completion_tokens = metadata.get("completion_tokens", 0)
        
        # Assume generic $10 / 1M input, $30 / 1M output for estimation purposes
        estimated_cost_usd = (prompt_tokens / 1000000.0) * 10.0 + (completion_tokens / 1000000.0) * 30.0
        
        log = ExtractionCostLog(
            job_id=job_id,
            provider=metadata.get("provider", "unknown"),
            model=metadata.get("model", "unknown"),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=metadata.get("total_tokens", 0),
            estimated_cost_usd=estimated_cost_usd,
            latency_ms=metadata.get("latency_ms", 0),
            extraction_type=extraction_type
        )
        self.session.add(log)
        await self.session.commit()
        
        # We could query SUM(estimated_cost_usd) WHERE job_id = job_id
        # and raise BudgetExceededException if it exceeds self.max_cost_per_job
        # logger.info(f"Cost logged: ${estimated_cost_usd:.4f} for Job {job_id}")
