import React from "react";
import { Skeleton } from "@/components/feedback/Skeleton";

export function MessageSkeleton({ role }: { role: "user" | "assistant" }) {
  const isUser = role === "user";

  return (
    <div className={`flex w-full mb-6 ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex max-w-[85%] ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        {/* Avatar Skeleton */}
        <div className={`flex-shrink-0 flex items-start ${isUser ? "ml-3" : "mr-3"}`}>
          <Skeleton className="w-8 h-8 rounded-full" />
        </div>

        {/* Message Body Skeleton */}
        <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
          <div className={`px-4 py-4 rounded-2xl w-48 sm:w-64 ${
            isUser ? "rounded-tr-sm bg-gray-100 dark:bg-gray-800/50" : "rounded-tl-sm border border-gray-100 dark:border-gray-800"
          }`}>
            <Skeleton className="w-full h-4 mb-2" />
            <Skeleton className="w-3/4 h-4" />
          </div>
        </div>
      </div>
    </div>
  );
}
