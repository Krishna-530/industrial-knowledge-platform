import React from "react";
import { Skeleton } from "@/components/feedback/Skeleton";

export function ConversationSidebarSkeleton() {
  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 w-full sm:w-64 flex-shrink-0">
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <Skeleton className="w-full h-10 rounded-md" />
      </div>
      <div className="flex-1 p-2 space-y-2 mt-2">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Skeleton key={i} className="w-full h-10 rounded-md" />
        ))}
      </div>
    </div>
  );
}
