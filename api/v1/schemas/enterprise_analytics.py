from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float

class DocumentAnalytics(BaseModel):
    total_documents: int
    upload_trends: List[TimeSeriesPoint]

class ProcessingAnalytics(BaseModel):
    queue_length: int
    failed_jobs: int
    average_processing_time_ms: float

class SearchAnalytics(BaseModel):
    search_count: int
    top_queries: List[str]
    zero_result_searches: int
    average_response_time_ms: float
    search_success_rate: float

class UserAnalytics(BaseModel):
    active_users: int

class StorageAnalytics(BaseModel):
    total_storage_bytes: int

class EnterpriseAnalyticsResponse(BaseModel):
    documents: DocumentAnalytics
    processing: ProcessingAnalytics
    search: SearchAnalytics
    users: UserAnalytics
    storage: StorageAnalytics
