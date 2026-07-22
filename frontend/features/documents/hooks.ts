import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentKeys } from "@/lib/query-keys";
import { getDocuments, deleteDocument, retryDocument } from "./api";
import type { DocumentListFilters } from "./types";
import { featureFlags } from "@/lib/feature-flags";
import { useDemoStore } from "@/lib/demo/useDemoStore";


export function useDocuments(filters: DocumentListFilters) {
  const filterKey = JSON.stringify(filters);
  // Always call hook unconditionally (React hooks rules) — result used only in DEMO_MODE
  const demoSnapshot = useDemoStore();

  return useQuery({
    queryKey: documentKeys.list(filterKey),
    queryFn: () => getDocuments(filters),
    staleTime: 30 * 1000,
    // In demo mode, seed the query with store data so the table is always populated
    ...(featureFlags.DEMO_MODE ? {
      initialData: (() => {
        const { documents } = demoSnapshot;
        const page = filters.page ?? 1;
        const pageSize = filters.pageSize ?? 20;
        const search = filters.search?.toLowerCase();
        const filtered = search ? documents.filter(d => d.filename.toLowerCase().includes(search)) : documents;
        const start = (page - 1) * pageSize;
        return {
          items: filtered.slice(start, start + pageSize).map(d => ({
            id: d.id, filename: d.filename, status: d.status as any,
            uploadedAt: d.uploadedAt, fileSize: d.fileSize, mimeType: d.mimeType,
            assetCount: d.entityCount, errorMessage: null, processedAt: d.uploadedAt,
          })),
          total: filtered.length,
          page,
          pageSize,
          totalPages: Math.ceil(filtered.length / pageSize),
        };
      })(),
      initialDataUpdatedAt: Date.now(),
    } : {}),
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
