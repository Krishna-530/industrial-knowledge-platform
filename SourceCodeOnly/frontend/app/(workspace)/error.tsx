"use client";

import { useEffect } from "react";

export default function WorkspaceError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Workspace rendering error:", error);
  }, [error]);

  return (
    <div className="flex h-full flex-col items-center justify-center p-8 bg-background">
      <div className="text-center max-w-md">
        <h2 className="text-xl font-semibold text-danger mb-2">Something went wrong</h2>
        <p className="text-muted text-sm mb-6">
          An error occurred while rendering this page.
        </p>
        <button
          onClick={() => reset()}
          className="px-4 py-2 bg-brand-500 text-white rounded-md font-medium shadow-sm hover:bg-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
