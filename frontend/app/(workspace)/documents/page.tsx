"use client";

import React, { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Download, Trash2, RefreshCw, Search, Upload } from "lucide-react";
import { useDocuments, useDeleteDocument, useRetryDocument } from "@/features/documents/hooks";
import { DocumentStatusBadge } from "@/features/documents/components/DocumentStatusBadge";
import { DocumentsSkeleton } from "@/features/documents/components/DocumentsSkeleton";
import { EmptyDocuments } from "@/features/documents/components/EmptyDocuments";
import { DemoUploadPanel } from "@/features/documents/components/DemoUploadPanel";
import { DataTable, type Column } from "@/components/ui/DataTable";
import { NetworkError } from "@/components/feedback/ErrorStates";
import { useToast } from "@/hooks/useToast";
import type { Document, DocumentStatus } from "@/features/documents/types";
import { featureFlags } from "@/lib/feature-flags";


function DocumentsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const toast = useToast();
  const [showDemoUpload, setShowDemoUpload] = useState(false);


  const page = parseInt(searchParams.get("page") || "1", 10);
  const search = searchParams.get("search") || "";
  const sort = searchParams.get("sort") || "uploaded_at";
  const direction = (searchParams.get("direction") as "asc" | "desc") || "desc";

  const [searchInput, setSearchInput] = useState(search);

  // 300ms Search Debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      const params = new URLSearchParams(searchParams.toString());
      if (searchInput) {
        params.set("search", searchInput);
        params.set("page", "1"); // Reset to page 1 on search
      } else {
        params.delete("search");
      }
      router.push(`?${params.toString()}`);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput, router, searchParams]);

  const { data, isLoading, isError, refetch } = useDocuments({
    page,
    pageSize: 20,
    search: search || undefined,
    sort,
    direction,
  });

  const deleteMutation = useDeleteDocument();
  const retryMutation = useRetryDocument();

  const handlePageChange = (newPage: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", newPage.toString());
    router.push(`?${params.toString()}`);
  };

  const handleSortChange = (key: string, newDirection: "asc" | "desc") => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("sort", key);
    params.set("direction", newDirection);
    router.push(`?${params.toString()}`);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this document? This action cannot be undone.")) {
      try {
        await deleteMutation.mutateAsync(id);
        toast.success("Document deleted successfully");
      } catch {
        toast.error("Failed to delete document");
      }
    }
  };

  const handleRetry = async (id: string) => {
    try {
      await retryMutation.mutateAsync(id);
      toast.success("Document processing restarted");
    } catch {
      toast.error("Failed to restart processing");
    }
  };

  const columns: Column<Document>[] = [
    {
      key: "filename",
      header: "Filename",
      sortable: true,
      render: (doc) => (
        <div className="font-medium text-gray-900 dark:text-gray-100">{doc.filename}</div>
      ),
    },
    {
      key: "status",
      header: "Status",
      sortable: true,
      render: (doc) => <DocumentStatusBadge status={doc.status} />,
    },
    {
      key: "assetCount",
      header: "Assets Extracted",
      sortable: true,
    },
    {
      key: "uploadedAt",
      header: "Date Uploaded",
      sortable: true,
      render: (doc) => new Date(doc.uploadedAt).toLocaleDateString(),
    },
  ];

  if (isError) {
    return <NetworkError onRetry={() => refetch()} />;
  }

  const toolbar = (
    <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
      <div className="relative w-full sm:w-96">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md leading-5 bg-white dark:bg-gray-900 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Search documents..."
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
      </div>
      <div className="flex items-center gap-3">
        {featureFlags.DEMO_MODE && (
          <button
            onClick={() => setShowDemoUpload(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors"
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload Document
          </button>
        )}
        <button
          onClick={() => refetch()}
          className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>
    </div>
  );


  const renderActions = (doc: Document) => (
    <div className="flex justify-end space-x-2">
      {doc.status === "failed" && (
        <button
          onClick={() => handleRetry(doc.id)}
          className="text-amber-600 hover:text-amber-900 dark:text-amber-400 dark:hover:text-amber-300 p-1"
          title="Retry Processing"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      )}
      <button
        onClick={() => handleDelete(doc.id)}
        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 p-1"
        title="Delete Document"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Documents</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Manage uploaded documents and monitor processing status.
        </p>
      </div>

      {/* Demo Upload Overlay */}
      {featureFlags.DEMO_MODE && showDemoUpload && (
        <div className="max-w-lg">
          <DemoUploadPanel onClose={() => setShowDemoUpload(false)} />
        </div>
      )}

      <DataTable
        columns={columns}
        rows={data?.items || []}
        rowKey="id"
        isLoading={isLoading}
        emptyState={<EmptyDocuments />}
        toolbar={toolbar}
        actions={renderActions}
        currentSort={{ key: sort, direction }}
        onSortChange={handleSortChange}
        pagination={{
          currentPage: page,
          totalPages: data?.totalPages || 1,
          onPageChange: handlePageChange,
        }}
      />
    </div>
  );
}


export default function DocumentsPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Suspense fallback={<DocumentsSkeleton />}>
        <DocumentsContent />
      </Suspense>
    </div>
  );
}
