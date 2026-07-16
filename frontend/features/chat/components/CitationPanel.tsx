import React from "react";
import { useCitation } from "../hooks/useCitation";
import { EvidenceCard } from "./EvidenceCard";
import { RelationshipCard } from "./RelationshipCard";
import { SourceDocumentCard } from "./SourceDocumentCard";
import { Loader2, AlertCircle } from "lucide-react";

interface CitationPanelProps {
  relationshipId: string;
}

export function CitationPanel({ relationshipId }: CitationPanelProps) {
  const { data, isLoading, isError, error } = useCitation(relationshipId);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-gray-500">
        <Loader2 className="w-8 h-8 animate-spin mb-4 text-blue-500" />
        <p className="text-sm">Retrieving provenance...</p>
      </div>
    );
  }

  if (isError || !data || data.traces.length === 0) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-sm">Evidence unavailable</h3>
            <p className="text-xs mt-1">
              The answer exists but supporting provenance could not be loaded.
              {error instanceof Error ? ` (${error.message})` : ""}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {data.traces.map((trace) => (
        <div key={trace.id} className="space-y-4 pb-6 border-b border-gray-100 dark:border-gray-800 last:border-0">
          <RelationshipCard relationshipId={trace.relationship_id} />
          
          <div className="space-y-4">
            {trace.supporting_chunks.map((chunk, idx) => (
              <div key={idx} className="space-y-2">
                <EvidenceCard 
                  textSnippet={chunk.text_snippet} 
                  confidenceScore={trace.confidence_score} 
                />
                <SourceDocumentCard 
                  documentId={chunk.document_id} 
                  chunkId={chunk.chunk_id} 
                />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
