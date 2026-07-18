export interface TimeSeriesPoint {
  timestamp: string;
  value: number;
}

export interface DocumentAnalytics {
  total_documents: number;
  upload_trends: TimeSeriesPoint[];
}

export interface ProcessingAnalytics {
  queue_length: number;
  failed_jobs: number;
  average_processing_time_ms: number;
}

export interface SearchAnalytics {
  search_count: number;
  top_queries: string[];
  zero_result_searches: number;
  average_response_time_ms: number;
  search_success_rate: number;
}

export interface UserAnalytics {
  active_users: number;
}

export interface StorageAnalytics {
  total_storage_bytes: number;
}

export interface EnterpriseAnalyticsResponse {
  documents: DocumentAnalytics;
  processing: ProcessingAnalytics;
  search: SearchAnalytics;
  users: UserAnalytics;
  storage: StorageAnalytics;
}

export interface Conflict {
  id: string;
  assetId?: string;
  severity?: string;
  status?: string;
  detectedAt?: string;
}

export interface Corroboration {
  id: string;
  assetId?: string;
  confidenceScore?: number;
  verifiedAt?: string;
}

export interface Duplicate {
  id: string;
  primaryAssetId?: string;
  similarityScore?: number;
  status?: string;
  detectedAt?: string;
}

export interface PaginatedConflicts {
  items: Conflict[];
  total: number;
  totalPages?: number;
}

export interface PaginatedCorroborations {
  items: Corroboration[];
  total: number;
  totalPages?: number;
}

export interface PaginatedDuplicates {
  items: Duplicate[];
  total: number;
  totalPages?: number;
}

export interface AnalyticsFilters {
  start_date?: string;
  end_date?: string;
  page?: number;
  pageSize?: number;
  search?: string;
  severity?: string;
  status?: string;
  sort?: string;
  direction?: string;
}
