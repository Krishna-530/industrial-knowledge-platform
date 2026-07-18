from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class ExecutionMetrics(BaseModel):
    tracking_id: UUID
    duration_ms: float
    retry_count: int
    success: bool
    error_type: Optional[str] = None
    timestamp: datetime

class ProviderMetrics(BaseModel):
    provider_name: str
    is_healthy: bool
    circuit_breaker_tripped: bool
    timestamp: datetime

class TokenMetrics(BaseModel):
    tracking_id: UUID
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: datetime

class CostMetrics(BaseModel):
    tracking_id: UUID
    model_name: str
    estimated_cost_usd: float
    timestamp: datetime

class LLMAuditEvent(BaseModel):
    tracking_id: UUID
    model_name: str
    provider_name: str
    timestamp: datetime
