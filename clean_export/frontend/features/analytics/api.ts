import { apiClient } from "@/lib/api-client";
import type { 
  Conflict, Corroboration, Duplicate, 
  PaginatedConflicts, PaginatedCorroborations, PaginatedDuplicates, 
  AnalyticsFilters 
} from "./types";

function mapConflict(raw: any): Conflict {
  return {
    id: String(raw.id),
    assetId: String(raw.asset_id),
    assetName: raw.asset_name ?? "Unknown Asset",
    attributeName: raw.attribute_name ?? "Unknown Attribute",
    conflictingValues: raw.conflicting_values ?? [],
    sourceDocumentIds: (raw.source_document_ids ?? []).map(String),
    severity: raw.severity ?? "low",
    detectedAt: raw.detected_at ?? new Date().toISOString(),
    status: raw.status ?? "active",
  };
}

function mapCorroboration(raw: any): Corroboration {
  return {
    id: String(raw.id),
    assetId: String(raw.asset_id),
    assetName: raw.asset_name ?? "Unknown Asset",
    attributeName: raw.attribute_name ?? "Unknown Attribute",
    verifiedValue: String(raw.verified_value ?? ""),
    sourceDocumentIds: (raw.source_document_ids ?? []).map(String),
    confidenceScore: raw.confidence_score ?? 0,
    verifiedAt: raw.verified_at ?? new Date().toISOString(),
  };
}

function mapDuplicate(raw: any): Duplicate {
  return {
    id: String(raw.id),
    primaryAssetId: String(raw.primary_asset_id),
    duplicateAssetIds: (raw.duplicate_asset_ids ?? []).map(String),
    similarityScore: raw.similarity_score ?? 0,
    detectedAt: raw.detected_at ?? new Date().toISOString(),
    status: raw.status ?? "pending",
  };
}

function buildParams(filters: AnalyticsFilters): URLSearchParams {
  const params = new URLSearchParams();
  if (filters.page) params.append("page", filters.page.toString());
  if (filters.pageSize) params.append("page_size", filters.pageSize.toString());
  if (filters.search) params.append("search", filters.search);
  if (filters.severity) params.append("severity", filters.severity);
  if (filters.status) params.append("status", filters.status);
  if (filters.sort) params.append("sort", filters.sort);
  if (filters.direction) params.append("direction", filters.direction);
  return params;
}

export async function getConflicts(filters: AnalyticsFilters): Promise<PaginatedConflicts> {
  const params = buildParams(filters);
  const data = await apiClient<any>({
    endpoint: `/analytics/conflicts?${params.toString()}`,
    method: "GET",
  });
  return {
    items: (data.items || []).map(mapConflict),
    total: data.total ?? 0,
    page: data.page ?? 1,
    pageSize: data.page_size ?? 20,
    totalPages: data.total_pages ?? 1,
  };
}

export async function getCorroborations(filters: AnalyticsFilters): Promise<PaginatedCorroborations> {
  const params = buildParams(filters);
  const data = await apiClient<any>({
    endpoint: `/analytics/corroborations?${params.toString()}`,
    method: "GET",
  });
  return {
    items: (data.items || []).map(mapCorroboration),
    total: data.total ?? 0,
    page: data.page ?? 1,
    pageSize: data.page_size ?? 20,
    totalPages: data.total_pages ?? 1,
  };
}

export async function getDuplicates(filters: AnalyticsFilters): Promise<PaginatedDuplicates> {
  const params = buildParams(filters);
  const data = await apiClient<any>({
    endpoint: `/analytics/duplicates?${params.toString()}`,
    method: "GET",
  });
  return {
    items: (data.items || []).map(mapDuplicate),
    total: data.total ?? 0,
    page: data.page ?? 1,
    pageSize: data.page_size ?? 20,
    totalPages: data.total_pages ?? 1,
  };
}
