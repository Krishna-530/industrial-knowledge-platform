"use client";

import React, { useState } from "react";
import { useAssetFacts } from "../hooks";
import { DataTable, type Column } from "@/components/ui/DataTable";
import type { Fact } from "../types";
import { NetworkError } from "@/components/feedback/ErrorStates";
import { FileText } from "lucide-react";

export function AssetFactsSection({ assetId }: { assetId: string }) {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError, refetch } = useAssetFacts(assetId, page, 10);

  if (isError) {
    return <NetworkError onRetry={() => refetch()} title="Failed to load facts" />;
  }

  const columns: Column<Fact>[] = [
    {
      key: "attributeName",
      header: "Attribute",
      render: (fact) => <span className="font-medium text-gray-900 dark:text-gray-100">{fact.attributeName}</span>,
    },
    {
      key: "attributeValue",
      header: "Value",
      render: (fact) => <span className="text-gray-700 dark:text-gray-300">{fact.attributeValue}</span>,
    },
    {
      key: "confidenceScore",
      header: "Confidence",
      render: (fact) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          fact.confidenceScore > 0.9 ? 'bg-emerald-100 text-emerald-800' :
          fact.confidenceScore > 0.7 ? 'bg-blue-100 text-blue-800' :
          'bg-amber-100 text-amber-800'
        }`}>
          {Math.round(fact.confidenceScore * 100)}%
        </span>
      ),
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow ring-1 ring-black ring-opacity-5">
      <div className="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-800 flex items-center">
        <FileText className="w-5 h-5 mr-2 text-gray-400" />
        <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-gray-100">
          Extracted Facts
        </h3>
      </div>
      <DataTable
        columns={columns}
        rows={data?.items || []}
        rowKey="id"
        isLoading={isLoading}
        emptyState={
          <div className="text-center py-8 text-gray-500">No facts extracted for this asset yet.</div>
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
