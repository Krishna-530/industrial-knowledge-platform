import React, { useEffect, useRef } from "react";
import { useCitationDrawerStore } from "../hooks/useCitation";
import { CitationPanel } from "./CitationPanel";
import { X } from "lucide-react";

export function CitationDrawer() {
  const { isOpen, activeRelationshipId, closeDrawer } = useCitationDrawerStore();
  const drawerRef = useRef<HTMLDivElement>(null);

  // Close on ESC
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape" && isOpen) {
        closeDrawer();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, closeDrawer]);

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/20 dark:bg-black/40 z-40 transition-opacity"
        onClick={closeDrawer}
        aria-hidden="true"
      />
      <div 
        ref={drawerRef}
        role="dialog"
        aria-modal="true"
        aria-label="Citation Evidence Drawer"
        className="fixed inset-y-0 right-0 w-full max-w-md bg-white dark:bg-gray-900 shadow-xl z-50 transform transition-transform duration-300 ease-in-out border-l border-gray-200 dark:border-gray-800 overflow-y-auto"
      >
        <div className="sticky top-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-800 px-4 py-3 flex items-center justify-between z-10">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Explainability</h2>
          <button
            onClick={closeDrawer}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Close drawer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {activeRelationshipId && (
          <CitationPanel relationshipId={activeRelationshipId} />
        )}
      </div>
    </>
  );
}
