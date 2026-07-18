import { apiClient } from "@/lib/api-client";
import type { 
  Asset, Fact, Finding, PaginatedAssets, PaginatedFacts, PaginatedFindings, AssetListFilters 
} from "./types";

function mapAsset(raw: any): Asset {
  return {
    id: String(raw.id),
    name: raw.name ?? "Unknown Asset",
    type: raw.type ?? "General",
    status: raw.status ?? "unknown",
    description: raw.description,
    confidenceScore: raw.confidence_score ?? 0,
    extractedAt: raw.extracted_at ?? new Date().toISOString(),
  };
}

function mapFact(raw: any): Fact {
  return {
    id: String(raw.id),
    assetId: String(raw.asset_id),
    attributeName: raw.attribute_name ?? "",
    attributeValue: raw.attribute_value ?? "",
    confidenceScore: raw.confidence_score ?? 0,
    sourceDocumentId: String(raw.source_document_id),
  };
}

function mapFinding(raw: any): Finding {
  return {
    id: String(raw.id),
    assetId: String(raw.asset_id),
    title: raw.title ?? "Unknown Finding",
    description: raw.description ?? "",
    severity: raw.severity ?? "low",
    status: raw.status ?? "open",
  };
}

export async function getAssets(filters: AssetListFilters): Promise<PaginatedAssets> {
  const params = new URLSearchParams();
  if (filters.page) params.append("page", filters.page.toString());
  if (filters.pageSize) params.append("page_size", filters.pageSize.toString());
  if (filters.search) params.append("search", filters.search);
  if (filters.status) params.append("status", filters.status);
  if (filters.sort) params.append("sort", filters.sort);
  if (filters.direction) params.append("direction", filters.direction);

  const data = await apiClient<any>({
    endpoint: `/assets?${params.toString()}`,
    method: "GET",
  });

  return {
    items: (data.items || []).map(mapAsset),
    total: data.total ?? 0,
    page: data.page ?? 1,
    pageSize: data.page_size ?? 20,
    totalPages: data.total_pages ?? 1,
  };
}

export async function getAssetDetails(id: string): Promise<Asset> {
  const data = await apiClient<any>({
    endpoint: `/assets/${id}`,
    method: "GET",
  });
  return mapAsset(data);
}

export async function getAssetFacts(id: string, page = 1, pageSize = 20): Promise<PaginatedFacts> {
  const data = await apiClient<any>({
    endpoint: `/assets/${id}/facts?page=${page}&page_size=${pageSize}`,
    method: "GET",
  });
  return {
    items: (data.items || []).map(mapFact),
    total: data.total ?? 0,
    page: data.page ?? 1,
    pageSize: data.page_size ?? 20,
    totalPages: data.total_pages ?? 1,
  };
}

export async function getAssetFindings(id: string, page = 1, pageSize = 20): Promise<PaginatedFindings> {
  const data = await apiClient<any>({
    endpoint: `/assets/${id}/findings?page=${page}&page_size=${pageSize}`,
    method: "GET",
  });
  return {
    items: (data.items || []).map(mapFinding),
    total: data.total ?? 0,
    page: data.page ?? 1,
    pageSize: data.page_size ?? 20,
    totalPages: data.total_pages ?? 1,
  };
}
