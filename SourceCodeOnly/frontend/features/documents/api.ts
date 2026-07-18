import { apiClient } from "@/lib/api-client";
import type { Document, PaginatedDocuments, DocumentListFilters } from "./types";

function mapDocument(raw: any): Document {
  return {
    id: String(raw.id),
    filename: raw.filename ?? "Unknown File",
    status: raw.status ?? "failed",
    uploadedAt: raw.uploaded_at ?? new Date().toISOString(),
    processedAt: raw.processed_at,
    fileSize: raw.file_size ?? 0,
    mimeType: raw.mime_type ?? "application/octet-stream",
    errorMessage: raw.error_message,
    assetCount: raw.asset_count ?? 0,
  };
}

export async function getDocuments(filters: DocumentListFilters): Promise<PaginatedDocuments> {
  const params = new URLSearchParams();
  if (filters.page) params.append("page", filters.page.toString());
  if (filters.pageSize) params.append("page_size", filters.pageSize.toString());
  if (filters.search) params.append("search", filters.search);
  if (filters.status) params.append("status", filters.status);
  if (filters.sort) params.append("sort", filters.sort);
  if (filters.direction) params.append("direction", filters.direction);

  const data = await apiClient<any>({
    endpoint: `/documents?${params.toString()}`,
    method: "GET",
  });

  return {
    items: (data.items || []).map(mapDocument),
    total: data.total ?? 0,
    page: data.page ?? 1,
    pageSize: data.page_size ?? 20,
    totalPages: data.total_pages ?? 1,
  };
}

export async function deleteDocument(id: string): Promise<void> {
  await apiClient<void>({
    endpoint: `/documents/${id}`,
    method: "DELETE",
  });
}

export async function retryDocument(id: string): Promise<void> {
  await apiClient<void>({
    endpoint: `/documents/${id}/retry`,
    method: "POST",
  });
}

export async function getDocumentChunks(id: string) {
  return await apiClient<any[]>({
    endpoint: `/documents/${id}/chunks`,
    method: "GET",
  });
}

export async function getDocumentEntities(id: string) {
  return await apiClient<any[]>({
    endpoint: `/documents/${id}/entities`,
    method: "GET",
  });
}

export async function getDocumentRelationships(id: string) {
  return await apiClient<any[]>({
    endpoint: `/documents/${id}/relationships`,
    method: "GET",
  });
}
