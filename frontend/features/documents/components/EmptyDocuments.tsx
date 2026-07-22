"use client";

import React, { useState } from "react";
import { FileUp } from "lucide-react";
import { featureFlags } from "@/lib/feature-flags";
import { DemoUploadPanel } from "./DemoUploadPanel";

export function EmptyDocuments() {
  const [showDemoUpload, setShowDemoUpload] = useState(false);

  if (featureFlags.DEMO_MODE && showDemoUpload) {
    return (
      <div className="p-6 max-w-lg mx-auto">
        <DemoUploadPanel onClose={() => setShowDemoUpload(false)} />
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-full mb-4">
        <FileUp className="w-10 h-10 text-blue-600 dark:text-blue-400" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Documents Yet</h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm mb-6">
        Upload your first engineering diagram, manual, or technical specification to begin extracting intelligence.
      </p>
      <button
        type="button"
        onClick={featureFlags.DEMO_MODE ? () => setShowDemoUpload(true) : undefined}
        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <FileUp className="w-4 h-4 mr-2" />
        Upload Document
      </button>
    </div>
  );
}
