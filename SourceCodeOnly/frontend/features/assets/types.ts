export interface Asset {
  id: string;
  name: string;
  type: string;
  status: "active" | "inactive" | "maintenance" | "unknown";
  description?: string;
  confidenceScore: number;
  extractedAt: string;
}

export interface Fact {
  id: string;
  assetId: string;
  attributeName: string;
  attributeValue: string;
  confidenceScore: number;
  sourceDocumentId: string;
}

export interface Finding {
  id: string;
  assetId: string;
  title: string;
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "open" | "resolved";
}

export interface PaginatedAssets {
  items: Asset[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface PaginatedFacts {
  items: Fact[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface PaginatedFindings {
  items: Finding[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface AssetListFilters {
  page?: number;
  pageSize?: number;
  search?: string;
  status?: string;
  sort?: string;
  direction?: "asc" | "desc";
}
