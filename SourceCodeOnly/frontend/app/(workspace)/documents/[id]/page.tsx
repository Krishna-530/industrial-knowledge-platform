import React from "react";
import { DocumentGraph } from "@/features/documents/components/DocumentGraph";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function DocumentExplorerPage({ params }: { params: { id: string } }) {
  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-gray-50 dark:bg-gray-900 p-6">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link 
            href="/documents" 
            className="p-2 bg-white dark:bg-gray-800 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white rounded-md border border-gray-200 dark:border-gray-700 shadow-sm"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
              Document Explorer
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Interactive structural knowledge graph for this document.
            </p>
          </div>
        </div>
      </div>
      
      <div className="flex-1 min-h-0 bg-white dark:bg-gray-950 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-4">
        <DocumentGraph documentId={params.id} />
      </div>
    </div>
  );
}
