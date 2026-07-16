import React from "react";
import { Cpu, ArrowLeft } from "lucide-react";
import Link from "next/link";
import type { Asset } from "../types";

export function AssetHeader({ asset }: { asset: Asset }) {
  return (
    <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-4 py-5 sm:px-6 mb-6 rounded-lg shadow-sm">
      <div className="mb-4">
        <Link 
          href="/assets" 
          className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Assets
        </Link>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="p-3 bg-purple-50 dark:bg-purple-900/30 rounded-lg mr-4">
            <Cpu className="w-8 h-8 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{asset.name}</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">{asset.type} • Extracted {new Date(asset.extractedAt).toLocaleDateString()}</p>
          </div>
        </div>
        <div>
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            asset.status === 'active' ? 'bg-emerald-100 text-emerald-800' :
            asset.status === 'maintenance' ? 'bg-amber-100 text-amber-800' :
            asset.status === 'inactive' ? 'bg-gray-100 text-gray-800' :
            'bg-red-100 text-red-800'
          }`}>
            {asset.status.charAt(0).toUpperCase() + asset.status.slice(1)}
          </span>
        </div>
      </div>
    </div>
  );
}
