import React from "react";
import { Cpu } from "lucide-react";

export function EmptyAssets() {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-full mb-4">
        <Cpu className="w-10 h-10 text-purple-600 dark:text-purple-400" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No Assets Discovered</h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm">
        The intelligence engine has not extracted any industrial assets yet. Upload engineering documents to begin extraction.
      </p>
    </div>
  );
}
