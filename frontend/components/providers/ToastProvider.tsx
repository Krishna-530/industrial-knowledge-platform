"use client";

import { ToastContainer } from "@/hooks/useToast";

export default function ToastProvider({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <div
        id="toast-container"
        aria-live="polite"
        aria-atomic="false"
        className="fixed bottom-4 right-4 z-toast flex flex-col gap-2 pointer-events-none"
      />
      <ToastContainer />
    </>
  );
}

