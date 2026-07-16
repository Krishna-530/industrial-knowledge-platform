"use client";

import React, { Suspense } from "react";
import { useAssetDetails } from "@/features/assets/hooks";
import { AssetHeader } from "@/features/assets/components/AssetHeader";
import { AssetMetadataCard } from "@/features/assets/components/AssetMetadataCard";
import { AssetFactsSection } from "@/features/assets/components/AssetFactsSection";
import { AssetFindingsSection } from "@/features/assets/components/AssetFindingsSection";
import { LinkedDocumentsSection } from "@/features/assets/components/LinkedDocumentsSection";
import { AssetDetailSkeleton } from "@/features/assets/components/AssetDetailSkeleton";
import { NetworkError } from "@/components/feedback/ErrorStates";

function AssetDetailContent({ id }: { id: string }) {
  const { data: asset, isLoading, isError, refetch } = useAssetDetails(id);

  if (isError) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <NetworkError onRetry={() => refetch()} title="Failed to load asset details" />
      </div>
    );
  }

  if (isLoading || !asset) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AssetDetailSkeleton />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <AssetHeader asset={asset} />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Identity propagation: AssetDetailContent acts as God container and delegates id */}
          <AssetFactsSection assetId={asset.id} />
          <AssetFindingsSection assetId={asset.id} />
        </div>
        
        <div className="space-y-8">
          <AssetMetadataCard asset={asset} />
          <LinkedDocumentsSection assetId={asset.id} />
        </div>
      </div>
    </div>
  );
}

export default function AssetDetailPage({ params }: { params: { id: string } }) {
  return (
    <Suspense fallback={<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"><AssetDetailSkeleton /></div>}>
      <AssetDetailContent id={params.id} />
    </Suspense>
  );
}
