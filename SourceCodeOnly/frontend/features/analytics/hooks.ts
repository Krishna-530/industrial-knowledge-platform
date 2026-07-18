import { useQuery } from "@tanstack/react-query";
import { analyticsKeys } from "@/lib/query-keys";
import { getConflicts, getCorroborations, getDuplicates } from "./api";
import type { AnalyticsFilters } from "./types";

export function useConflicts(filters: AnalyticsFilters) {
  const filterKey = JSON.stringify(filters);
  
  return useQuery({
    queryKey: analyticsKeys.conflicts(filterKey),
    queryFn: () => getConflicts(filters),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCorroborations(filters: AnalyticsFilters) {
  const filterKey = JSON.stringify(filters);
  
  return useQuery({
    queryKey: analyticsKeys.corroborations(filterKey),
    queryFn: () => getCorroborations(filters),
    staleTime: 5 * 60 * 1000,
  });
}

export function useDuplicates(filters: AnalyticsFilters) {
  const filterKey = JSON.stringify(filters);
  
  return useQuery({
    queryKey: analyticsKeys.duplicates(filterKey),
    queryFn: () => getDuplicates(filters),
    staleTime: 5 * 60 * 1000,
  });
}
