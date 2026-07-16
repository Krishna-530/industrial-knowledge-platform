import React from "react";
import { Info } from "lucide-react";
import type { Asset } from "../types";

export function AssetMetadataCard({ asset }: { asset: Asset }) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow ring-1 ring-black ring-opacity-5">
      <div className="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-800 flex items-center">
        <Info className="w-5 h-5 mr-2 text-gray-400" />
        <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-gray-100">
          Asset Metadata
        </h3>
      </div>
      <div className="px-4 py-5 sm:p-0">
        <dl className="sm:divide-y sm:divide-gray-200 dark:sm:divide-gray-800">
          <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Description</dt>
            <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 sm:mt-0 sm:col-span-2">
              {asset.description || "No description provided."}
            </dd>
          </div>
          <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Confidence Score</dt>
            <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 sm:mt-0 sm:col-span-2">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                asset.confidenceScore > 0.9 ? 'bg-emerald-100 text-emerald-800' :
                asset.confidenceScore > 0.7 ? 'bg-blue-100 text-blue-800' :
                'bg-amber-100 text-amber-800'
              }`}>
                {Math.round(asset.confidenceScore * 100)}%
              </span>
            </dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
