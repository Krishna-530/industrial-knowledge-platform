import React from "react";
import { CheckCircle } from "lucide-react";

export function EmptyAnalytics({ type }: { type: "conflicts" | "corroborations" | "duplicates" }) {
  const content = {
    conflicts: {
      title: "No Data Conflicts",
      desc: "Great news! The intelligence engine hasn't detected any conflicting information across your assets."
    },
    corroborations: {
      title: "No Verified Corroborations",
      desc: "There are currently no cross-verified facts across multiple documents."
    },
    duplicates: {
      title: "No Duplicate Assets",
      desc: "The system hasn't identified any duplicate assets requiring merging."
    }
  };

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="bg-emerald-50 dark:bg-emerald-900/30 p-4 rounded-full mb-4">
        <CheckCircle className="w-10 h-10 text-emerald-600 dark:text-emerald-400" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
        {content[type].title}
      </h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm">
        {content[type].desc}
      </p>
    </div>
  );
}
