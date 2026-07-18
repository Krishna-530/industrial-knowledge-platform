from pydantic import BaseModel
from typing import List, Optional, Generic, TypeVar
from database.models.intelligence_finding import FindingType
from uuid import UUID

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[str] = None
    has_more: bool = False

class AnalyticsSummary(BaseModel):
    total_active_facts: int
    total_conflicts: int
    total_corroborations: int
    total_duplicate_records: int
    
class FindingSummary(BaseModel):
    id: UUID
    type: FindingType
    asset_id: str
    property: str
    affected_fact_ids: List[str]

class ExtractedFactSummary(BaseModel):
    id: UUID
    asset_id: str
    property: str
    value: str
    document_id: UUID

class AssetAnalytics(BaseModel):
    asset_id: str
    findings: PaginatedResponse[FindingSummary]
    facts: PaginatedResponse[ExtractedFactSummary]
