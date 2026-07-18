import React from "react";
import { FileText } from "lucide-react";

interface SourceDocumentCardProps {
  documentId: string;
  chunkId: string;
}

export function SourceDocumentCard({ documentId, chunkId }: SourceDocumentCardProps) {
  return (
    <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 border border-gray-200 dark:border-gray-700 flex items-start gap-3">
      <div className="p-2 bg-white dark:bg-gray-800 rounded shadow-sm">
        <FileText className="w-5 h-5 text-gray-500" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
          Source Document
        </p>
        <p className="text-xs text-gray-500 font-mono mt-1 truncate">Doc: {documentId}</p>
        <p className="text-xs text-gray-500 font-mono truncate">Chunk: {chunkId}</p>
      </div>
    </div>
  );
}
