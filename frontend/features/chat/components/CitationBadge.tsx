import React from "react";
import { useCitationDrawerStore } from "../hooks/useCitation";

interface CitationBadgeProps {
  relationshipId: string;
  index?: number;
}

export function CitationBadge({ relationshipId, index }: CitationBadgeProps) {
  const { openDrawer } = useCitationDrawerStore();

  return (
    <button
      onClick={() => openDrawer(relationshipId)}
      className="inline-flex items-center justify-center px-1.5 py-0.5 mx-0.5 text-xs font-semibold text-blue-700 bg-blue-100 rounded hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
      aria-label={`View citation source ${index ? index : ""}`}
      title="View supporting evidence"
    >
      [{index ?? "src"}]
    </button>
  );
}
