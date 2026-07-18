import { useQuery } from "@tanstack/react-query";
import { assetKeys } from "@/lib/query-keys";
import { getAssets, getAssetDetails, getAssetFacts, getAssetFindings } from "./api";
import type { AssetListFilters } from "./types";

export function useAssets(filters: AssetListFilters) {
  const filterKey = JSON.stringify(filters);
  
  return useQuery({
    queryKey: assetKeys.list(filterKey),
    queryFn: () => getAssets(filters),
    staleTime: 5 * 60 * 1000,
  });
}

export function useAssetDetails(id: string) {
  return useQuery({
    queryKey: assetKeys.detail(id),
    queryFn: () => getAssetDetails(id),
    staleTime: 5 * 60 * 1000,
    enabled: !!id,
  });
}

export function useAssetFacts(id: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [...assetKeys.facts(id), { page, pageSize }] as const,
    queryFn: () => getAssetFacts(id, page, pageSize),
    staleTime: 5 * 60 * 1000,
    enabled: !!id,
  });
}

export function useAssetFindings(id: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [...assetKeys.findings(id), { page, pageSize }] as const,
    queryFn: () => getAssetFindings(id, page, pageSize),
    staleTime: 5 * 60 * 1000,
    enabled: !!id,
  });
}
