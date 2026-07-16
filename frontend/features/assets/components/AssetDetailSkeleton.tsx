import React from "react";
import { Skeleton } from "@/components/feedback/Skeleton";

export function AssetDetailSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="w-full h-32" />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Skeleton className="w-full h-64" />
          <Skeleton className="w-full h-64" />
        </div>
        <div className="space-y-6">
          <Skeleton className="w-full h-96" />
        </div>
      </div>
    </div>
  );
}
