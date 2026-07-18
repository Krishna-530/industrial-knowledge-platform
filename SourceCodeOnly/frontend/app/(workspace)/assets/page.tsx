"use client";

import React, { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Search, ChevronRight } from "lucide-react";
import Link from "next/link";
import { useAssets } from "@/features/assets/hooks";
import { AssetsSkeleton } from "@/features/assets/components/AssetsSkeleton";
import { EmptyAssets } from "@/features/assets/components/EmptyAssets";
import { DataTable, type Column } from "@/components/ui/DataTable";
import { NetworkError } from "@/components/feedback/ErrorStates";
import type { Asset } from "@/features/assets/types";

function AssetsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const page = parseInt(searchParams.get("page") || "1", 10);
  const search = searchParams.get("search") || "";
  const sort = searchParams.get("sort") || "extracted_at";
  const direction = (searchParams.get("direction") as "asc" | "desc") || "desc";

  const [searchInput, setSearchInput] = useState(search);

  // 300ms Search Debounce
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

  const { data, isLoading, isError, refetch } = useAssets({
    page,
    pageSize: 20,
    search: search || undefined,
    sort,
    direction,
  });

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

  const columns: Column<Asset>[] = [
    {
      key: "name",
      header: "Asset Name",
      sortable: true,
      render: (asset) => (
        <Link href={`/assets/${asset.id}`} className="font-medium text-blue-600 dark:text-blue-400 hover:underline">
          {asset.name}
        </Link>
      ),
    },
    {
      key: "type",
      header: "Type",
      sortable: true,
    },
    {
      key: "status",
      header: "Status",
      sortable: true,
      render: (asset) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          asset.status === 'active' ? 'bg-emerald-100 text-emerald-800' :
          asset.status === 'maintenance' ? 'bg-amber-100 text-amber-800' :
          asset.status === 'inactive' ? 'bg-gray-100 text-gray-800' :
          'bg-red-100 text-red-800'
        }`}>
          {asset.status.charAt(0).toUpperCase() + asset.status.slice(1)}
        </span>
      ),
    },
    {
      key: "confidenceScore",
      header: "Confidence",
      sortable: true,
      render: (asset) => `${Math.round(asset.confidenceScore * 100)}%`,
    },
    {
      key: "extractedAt",
      header: "Discovered",
      sortable: true,
      render: (asset) => new Date(asset.extractedAt).toLocaleDateString(),
    },
  ];

  const renderActions = (asset: Asset) => (
    <Link
      href={`/assets/${asset.id}`}
      className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 flex items-center justify-end"
    >
      <span className="sr-only">View</span>
      <ChevronRight className="w-5 h-5" />
    </Link>
  );

  const toolbar = (
    <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
      <div className="relative w-full sm:w-96">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md leading-5 bg-white dark:bg-gray-900 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Search assets..."
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
      </div>
    </div>
  );

  if (isError) {
    return <NetworkError onRetry={() => refetch()} />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Asset Explorer</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Explore and analyze industrial assets extracted from your engineering documents.
        </p>
      </div>

      <DataTable
        columns={columns}
        rows={data?.items || []}
        rowKey="id"
        isLoading={isLoading}
        emptyState={<EmptyAssets />}
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

export default function AssetsPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Suspense fallback={<AssetsSkeleton />}>
        <AssetsContent />
      </Suspense>
    </div>
  );
}
