import React from "react";
import { Link2 } from "lucide-react";
import Link from "next/link";
import type { Asset } from "../types";

export function LinkedDocumentsSection({ assetId }: { assetId: string }) {
  // For Phase 11.2.3, we'll implement a simple placeholder since linked documents 
  // might require a separate API or it could be derived from the facts/findings source_document_id.
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow ring-1 ring-black ring-opacity-5">
      <div className="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-800 flex items-center">
        <Link2 className="w-5 h-5 mr-2 text-gray-400" />
        <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-gray-100">
          Source Documents
        </h3>
      </div>
      <div className="p-4 text-center text-sm text-gray-500">
        <p className="mb-4">Documents that contributed to the extraction of this asset will appear here.</p>
        <Link 
          href="/documents"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
        >
          View All Documents
        </Link>
      </div>
    </div>
  );
}
