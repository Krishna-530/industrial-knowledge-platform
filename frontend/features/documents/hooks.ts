import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentKeys } from "@/lib/query-keys";
import { getDocuments, deleteDocument, retryDocument } from "./api";
import type { DocumentListFilters } from "./types";

export function useDocuments(filters: DocumentListFilters) {
  // We stringify the filters to create a stable query key for React Query
  const filterKey = JSON.stringify(filters);
  
  return useQuery({
    queryKey: documentKeys.list(filterKey),
    queryFn: () => getDocuments(filters),
    // Status can change as background workers process documents
    staleTime: 30 * 1000, 
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteDocument(id),
    onSuccess: () => {
      // Invalidate all document lists to refresh the table
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
      // Invalidate dashboard stats since we deleted a document
      queryClient.invalidateQueries({ queryKey: ["dashboard"] }); 
    },
  });
}

export function useRetryDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => retryDocument(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(id) });
    },
  });
}

export function useDocumentGraph(documentId: string) {
  return useQuery({
    queryKey: [...documentKeys.detail(documentId), "graph"],
    queryFn: async () => {
      const [chunks, entities, relationships] = await Promise.all([
        import("./api").then(m => m.getDocumentChunks(documentId)),
        import("./api").then(m => m.getDocumentEntities(documentId)),
        import("./api").then(m => m.getDocumentRelationships(documentId))
      ]);
      return { chunks, entities, relationships };
    },
    enabled: !!documentId,
    staleTime: 60 * 1000,
  });
}
