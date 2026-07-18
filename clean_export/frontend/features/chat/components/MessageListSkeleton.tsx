import React from "react";
import { MessageSkeleton } from "./MessageSkeleton";

export function MessageListSkeleton() {
  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
      <MessageSkeleton role="assistant" />
      <MessageSkeleton role="user" />
      <MessageSkeleton role="assistant" />
    </div>
  );
}
