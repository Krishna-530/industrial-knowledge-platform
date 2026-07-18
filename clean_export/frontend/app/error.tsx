"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("Global infrastructure error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4 bg-background text-foreground">
      <div className="flex flex-col items-center max-w-md text-center space-y-4">
        <h2 className="text-2xl font-semibold tracking-tight text-danger">Critical Application Error</h2>
        <p className="text-muted text-sm">
          The application encountered an unexpected infrastructure failure and could not recover.
        </p>
        <div className="flex gap-4">
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-brand-500 text-white rounded-md font-medium shadow-sm hover:bg-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
          >
            Reload Page
          </button>
        </div>
      </div>
    </div>
  );
}
