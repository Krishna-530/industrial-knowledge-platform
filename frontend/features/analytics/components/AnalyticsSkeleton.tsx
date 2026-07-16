import React from "react";
import { Skeleton } from "@/components/feedback/Skeleton";

export function AnalyticsSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
        <div>
          <Skeleton className="w-64 h-8" />
          <Skeleton className="w-96 h-4 mt-2" />
        </div>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-800">
        <nav className="-mb-px flex space-x-8">
          <Skeleton className="w-24 h-8 mb-2" />
          <Skeleton className="w-24 h-8 mb-2" />
          <Skeleton className="w-24 h-8 mb-2" />
        </nav>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm ring-1 ring-black ring-opacity-5">
        <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex justify-between">
          <Skeleton className="w-64 h-10" />
          <Skeleton className="w-24 h-10" />
        </div>
        <div className="p-4 space-y-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="w-full h-12" />
          ))}
        </div>
      </div>
    </div>
  );
}
