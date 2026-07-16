import React from "react";
import { ArrowRight } from "lucide-react";

interface RelationshipCardProps {
  relationshipId: string;
}

export function RelationshipCard({ relationshipId }: RelationshipCardProps) {
  return (
    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-100 dark:border-blue-800 mb-4">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-blue-900 dark:text-blue-200">Knowledge Graph Edge</span>
      </div>
      <div className="mt-2 flex items-center justify-center gap-2 text-xs font-mono bg-white dark:bg-gray-900 p-2 rounded border border-gray-200 dark:border-gray-700">
        <span className="text-gray-600 dark:text-gray-400">Subject</span>
        <ArrowRight className="w-4 h-4 text-blue-500" />
        <span className="text-blue-600 dark:text-blue-400 font-bold px-2 py-0.5 bg-blue-100 dark:bg-blue-900/50 rounded">
          RELATES_TO
        </span>
        <ArrowRight className="w-4 h-4 text-blue-500" />
        <span className="text-gray-600 dark:text-gray-400">Object</span>
      </div>
      <div className="mt-2 text-xs text-gray-500 text-center">Edge ID: {relationshipId}</div>
    </div>
  );
}
