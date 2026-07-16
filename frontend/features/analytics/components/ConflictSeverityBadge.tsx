import React from "react";
import { AlertCircle, AlertTriangle, Info, Skull } from "lucide-react";

interface ConflictSeverityBadgeProps {
  severity: "low" | "medium" | "high" | "critical";
}

export function ConflictSeverityBadge({ severity }: ConflictSeverityBadgeProps) {
  switch (severity) {
    case "critical":
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300">
          <Skull className="w-3.5 h-3.5 mr-1" />
          Critical
        </span>
      );
    case "high":
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300">
          <AlertCircle className="w-3.5 h-3.5 mr-1" />
          High
        </span>
      );
    case "medium":
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">
          <AlertTriangle className="w-3.5 h-3.5 mr-1" />
          Medium
        </span>
      );
    case "low":
    default:
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
          <Info className="w-3.5 h-3.5 mr-1" />
          Low
        </span>
      );
  }
}
