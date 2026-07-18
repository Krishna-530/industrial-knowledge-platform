import React from "react";

interface EvidenceCardProps {
  textSnippet: string;
  confidenceScore: number;
  provider?: string;
  model?: string;
  timestamp?: string;
}

export function EvidenceCard({
  textSnippet,
  confidenceScore,
  provider = "Neo4j Graph API",
  model = "Extracted Edge",
  timestamp = new Date().toISOString().split("T")[0],
}: EvidenceCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700 mb-4">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Supporting Evidence</h3>
      <blockquote className="text-sm text-gray-700 dark:text-gray-300 italic border-l-4 border-blue-500 pl-3 mb-4">
        "{textSnippet}"
      </blockquote>
      <div className="grid grid-cols-2 gap-2 text-xs text-gray-500 dark:text-gray-400">
        <div>
          <span className="font-medium">Confidence:</span> {(confidenceScore * 100).toFixed(1)}%
        </div>
        <div>
          <span className="font-medium">Provider:</span> {provider}
        </div>
        <div>
          <span className="font-medium">Model:</span> {model}
        </div>
        <div>
          <span className="font-medium">Extracted:</span> {timestamp}
        </div>
      </div>
    </div>
  );
}
