export interface DashboardStats {
  total_documents: number;
  total_assets: number;
  active_conflicts: number;
  processing_jobs: number;
  total_chunks: number;
  total_entities: number;
  total_relationships: number;
}

export interface KnowledgeGraphStats {
  total_nodes: number;
  total_edges: number;
  sync_lag: number | null;
  status: string;
}

export interface WorkerQueueStats {
  queued: number;
  processing: number;
  completed: number;
  failed: number;
  total: number;
}

export interface RetrievalStats {
  total_searches: number | null;
  average_latency: number | null;
  status: string;
}

export interface RecentDocument {
  id: string;
  title: string;
  status: string;
  uploaded_at: string;
}

export interface ProcessingQueueItem {
  job_id: string;
  job_type: string;
  status: string;
  started_at: string | null;
}

export interface DashboardOverviewResponse {
  stats: DashboardStats;
  graph: KnowledgeGraphStats;
  workers: WorkerQueueStats;
  retrieval: RetrievalStats;
  recent_documents: RecentDocument[];
  processing_queue: ProcessingQueueItem[];
}
