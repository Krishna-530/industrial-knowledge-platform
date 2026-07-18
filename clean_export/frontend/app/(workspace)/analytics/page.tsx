"use client";

import React, { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Search, ShieldAlert, CheckCircle, Copy } from "lucide-react";
import { useConflicts, useCorroborations, useDuplicates } from "@/features/analytics/hooks";
import { ConflictSeverityBadge } from "@/features/analytics/components/ConflictSeverityBadge";
import { AnalyticsSkeleton } from "@/features/analytics/components/AnalyticsSkeleton";
import { EmptyAnalytics } from "@/features/analytics/components/EmptyAnalytics";
import { DataTable, type Column } from "@/components/ui/DataTable";
import { NetworkError } from "@/components/feedback/ErrorStates";
import type { Conflict, Corroboration, Duplicate } from "@/features/analytics/types";

type Tab = "conflicts" | "corroborations" | "duplicates";

function AnalyticsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const currentTab = (searchParams.get("tab") as Tab) || "conflicts";
  const page = parseInt(searchParams.get("page") || "1", 10);
  const search = searchParams.get("search") || "";
  const sort = searchParams.get("sort") || "";
  const direction = (searchParams.get("direction") as "asc" | "desc") || "desc";

  const [searchInput, setSearchInput] = useState(search);

  useEffect(() => {
    const timer = setTimeout(() => {
      const params = new URLSearchParams(searchParams.toString());
      if (searchInput) {
        params.set("search", searchInput);
        params.set("page", "1");
      } else {
        params.delete("search");
      }
      router.push(`?${params.toString()}`);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput, router, searchParams]);

  const conflictsQuery = useConflicts({ page, search, sort, direction });
  const corroborationsQuery = useCorroborations({ page, search, sort, direction });
  const duplicatesQuery = useDuplicates({ page, search, sort, direction });

  const handleTabChange = (tab: Tab) => {
    setSearchInput("");
    router.push(`?tab=${tab}&page=1`);
  };

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

  const conflictColumns: Column<Conflict>[] = [
    { key: "assetName", header: "Asset", sortable: true },
    { key: "attributeName", header: "Attribute", sortable: true },
    { key: "severity", header: "Severity", sortable: true, render: (row) => <ConflictSeverityBadge severity={row.severity} /> },
    { key: "status", header: "Status", sortable: true, render: (row) => <span className="capitalize">{row.status}</span> },
    { key: "detectedAt", header: "Detected", sortable: true, render: (row) => new Date(row.detectedAt).toLocaleDateString() },
  ];

  const corroborationColumns: Column<Corroboration>[] = [
    { key: "assetName", header: "Asset", sortable: true },
    { key: "attributeName", header: "Attribute", sortable: true },
    { key: "verifiedValue", header: "Verified Value", sortable: true },
    { key: "confidenceScore", header: "Confidence", sortable: true, render: (row) => `${Math.round(row.confidenceScore * 100)}%` },
    { key: "verifiedAt", header: "Verified", sortable: true, render: (row) => new Date(row.verifiedAt).toLocaleDateString() },
  ];

  const duplicateColumns: Column<Duplicate>[] = [
    { key: "primaryAssetId", header: "Primary Asset ID", sortable: true },
    { key: "similarityScore", header: "Similarity", sortable: true, render: (row) => `${Math.round(row.similarityScore * 100)}%` },
    { key: "status", header: "Status", sortable: true, render: (row) => <span className="capitalize">{row.status}</span> },
    { key: "detectedAt", header: "Detected", sortable: true, render: (row) => new Date(row.detectedAt).toLocaleDateString() },
  ];

  const renderActiveTable = () => {
    if (currentTab === "conflicts") {
      if (conflictsQuery.isError) return <NetworkError onRetry={() => conflictsQuery.refetch()} />;
      return (
        <DataTable
          columns={conflictColumns}
          rows={conflictsQuery.data?.items || []}
          rowKey="id"
          isLoading={conflictsQuery.isLoading}
          emptyState={<EmptyAnalytics type="conflicts" />}
          currentSort={{ key: sort, direction }}
          onSortChange={handleSortChange}
          pagination={{ currentPage: page, totalPages: conflictsQuery.data?.totalPages || 1, onPageChange: handlePageChange }}
        />
      );
    }
    
    if (currentTab === "corroborations") {
      if (corroborationsQuery.isError) return <NetworkError onRetry={() => corroborationsQuery.refetch()} />;
      return (
        <DataTable
          columns={corroborationColumns}
          rows={corroborationsQuery.data?.items || []}
          rowKey="id"
          isLoading={corroborationsQuery.isLoading}
          emptyState={<EmptyAnalytics type="corroborations" />}
          currentSort={{ key: sort, direction }}
          onSortChange={handleSortChange}
          pagination={{ currentPage: page, totalPages: corroborationsQuery.data?.totalPages || 1, onPageChange: handlePageChange }}
        />
      );
    }
    
    if (duplicatesQuery.isError) return <NetworkError onRetry={() => duplicatesQuery.refetch()} />;
    return (
      <DataTable
        columns={duplicateColumns}
        rows={duplicatesQuery.data?.items || []}
        rowKey="id"
        isLoading={duplicatesQuery.isLoading}
        emptyState={<EmptyAnalytics type="duplicates" />}
        currentSort={{ key: sort, direction }}
        onSortChange={handleSortChange}
        pagination={{ currentPage: page, totalPages: duplicatesQuery.data?.totalPages || 1, onPageChange: handlePageChange }}
      />
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Knowledge Analytics</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Explore data discrepancies, verified facts, and duplicate entities detected by the engine.
        </p>
      </div>

      <div className="border-b border-gray-200 dark:border-gray-800">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => handleTabChange("conflicts")}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
              currentTab === "conflicts"
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:hover:text-gray-300"
            }`}
          >
            <ShieldAlert className="w-4 h-4 mr-2" />
            Data Conflicts
          </button>
          <button
            onClick={() => handleTabChange("corroborations")}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
              currentTab === "corroborations"
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:hover:text-gray-300"
            }`}
          >
            <CheckCircle className="w-4 h-4 mr-2" />
            Corroborations
          </button>
          <button
            onClick={() => handleTabChange("duplicates")}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
              currentTab === "duplicates"
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:hover:text-gray-300"
            }`}
          >
            <Copy className="w-4 h-4 mr-2" />
            Duplicates
          </button>
        </nav>
      </div>

      <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
        <div className="relative w-full sm:w-96">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md leading-5 bg-white dark:bg-gray-900 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder={`Search ${currentTab}...`}
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
        </div>
      </div>

      {renderActiveTable()}
    </div>
  );
}

export default function AnalyticsPage() {
  return (
    <Suspense fallback={<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"><AnalyticsSkeleton /></div>}>
      <AnalyticsContent />
    </Suspense>
  );
}
