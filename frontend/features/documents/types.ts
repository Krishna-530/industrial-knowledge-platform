export type DocumentStatus = "uploaded" | "processing" | "extracted" | "failed";

export interface Document {
  id: string;
  filename: string;
  status: DocumentStatus;
  uploadedAt: string;
  processedAt?: string;
  fileSize: number;
  mimeType: string;
  errorMessage?: string;
  assetCount: number;
}

export interface PaginatedDocuments {
  items: Document[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface DocumentListFilters {
  page?: number;
  pageSize?: number;
  search?: string;
  status?: DocumentStatus;
  sort?: string;
  direction?: "asc" | "desc";
}

export interface ExplorerChunk {
  id: string;
  index: number;
  text: string;
  token_count?: number;
  embedding_status: string;
}

export interface ExplorerEntity {
  id: string;
  name: string;
  category: string;
  confidence: number;
}

export interface ExplorerRelationship {
  id: string;
  subject_id: string;
  subject_name: string;
  predicate: string;
  object_id: string;
  object_name: string;
  quality_score: number;
  status: string;
}

export interface DocumentGraphData {
  chunks: ExplorerChunk[];
  entities: ExplorerEntity[];
  relationships: ExplorerRelationship[];
}
