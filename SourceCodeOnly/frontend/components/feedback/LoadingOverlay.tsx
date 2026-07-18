"use client";

import React from "react";
import { SpinnerIcon } from "@/lib/icons";

export default function LoadingOverlay() {
  return (
    <div className="fixed inset-0 z-overlay flex flex-col items-center justify-center bg-background">
      <SpinnerIcon className="h-10 w-10 animate-spin text-brand-500 mb-4" />
      <p className="text-muted text-sm font-medium animate-pulse-soft">Loading platform...</p>
    </div>
  );
}
