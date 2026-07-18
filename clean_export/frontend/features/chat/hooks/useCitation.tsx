import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import React, { createContext, useContext, useState, ReactNode } from "react";

export interface CitationChunk {
  chunk_id: string;
  document_id: string;
  text_snippet: string;
  score: number;
}

export interface ProvenanceTrace {
  id: string;
  relationship_id: string;
  confidence_score: number;
  supporting_chunks: CitationChunk[];
}

export interface EvidenceResponse {
  traces: ProvenanceTrace[];
}

interface CitationDrawerState {
  isOpen: boolean;
  activeRelationshipId: string | null;
  openDrawer: (relationshipId: string) => void;
  closeDrawer: () => void;
}

const CitationDrawerContext = createContext<CitationDrawerState | undefined>(undefined);

export function CitationDrawerProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeRelationshipId, setActiveRelationshipId] = useState<string | null>(null);

  const openDrawer = (id: string) => {
    setActiveRelationshipId(id);
    setIsOpen(true);
  };

  const closeDrawer = () => {
    setIsOpen(false);
    setActiveRelationshipId(null);
  };

  return (
    <CitationDrawerContext.Provider value={{ isOpen, activeRelationshipId, openDrawer, closeDrawer }}>
      {children}
    </CitationDrawerContext.Provider>
  );
}

export function useCitationDrawerStore(): CitationDrawerState {
  const context = useContext(CitationDrawerContext);
  if (context === undefined) {
    throw new Error("useCitationDrawerStore must be used within a CitationDrawerProvider");
  }
  return context;
}

export function useCitation(relationshipId: string | null) {
  return useQuery({
    queryKey: ["evidence", relationshipId],
    queryFn: async () => {
      if (!relationshipId) throw new Error("No relationship ID");
      const data = await apiClient<EvidenceResponse>({
        endpoint: `/graph/evidence/${relationshipId}`,
        method: "GET",
      });
      return data;
    },
    enabled: !!relationshipId,
    staleTime: 5 * 60 * 1000, // 5 minutes cache
  });
}
