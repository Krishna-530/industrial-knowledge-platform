"use client";

import React, { useState } from "react";
import { useAssetFindings } from "../hooks";
import { DataTable, type Column } from "@/components/ui/DataTable";
import type { Finding } from "../types";
import { NetworkError } from "@/components/feedback/ErrorStates";
import { AlertTriangle } from "lucide-react";

export function AssetFindingsSection({ assetId }: { assetId: string }) {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError, refetch } = useAssetFindings(assetId, page, 10);

  if (isError) {
    return <NetworkError onRetry={() => refetch()} title="Failed to load findings" />;
  }

  const columns: Column<Finding>[] = [
    {
      key: "title",
      header: "Finding",
      render: (finding) => (
        <div>
          <div className="font-medium text-gray-900 dark:text-gray-100">{finding.title}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">{finding.description}</div>
        </div>
      ),
    },
    {
      key: "severity",
      header: "Severity",
      render: (finding) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          finding.severity === 'critical' ? 'bg-red-100 text-red-800' :
          finding.severity === 'high' ? 'bg-orange-100 text-orange-800' :
          finding.severity === 'medium' ? 'bg-amber-100 text-amber-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {finding.severity.charAt(0).toUpperCase() + finding.severity.slice(1)}
        </span>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (finding) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          finding.status === 'open' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
        }`}>
          {finding.status.charAt(0).toUpperCase() + finding.status.slice(1)}
        </span>
      ),
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow ring-1 ring-black ring-opacity-5">
      <div className="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-800 flex items-center">
        <AlertTriangle className="w-5 h-5 mr-2 text-gray-400" />
        <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-gray-100">
          Identified Findings
        </h3>
      </div>
      <DataTable
        columns={columns}
        rows={data?.items || []}
        rowKey="id"
        isLoading={isLoading}
        emptyState={
          <div className="text-center py-8 text-gray-500">No findings identified for this asset.</div>
        }
        pagination={{
          currentPage: page,
          totalPages: data?.totalPages || 1,
          onPageChange: setPage,
        }}
      />
    </div>
  );
}
