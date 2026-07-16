"use client";

import { useEffect, useState, useCallback } from "react";
import { createPortal } from "react-dom";
import { CheckIcon, AlertCircleIcon, InfoIcon, AlertTriangleIcon, CloseIcon } from "@/lib/icons";

type ToastType = "success" | "error" | "info" | "warning";

interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

// Module-scoped state for global toast queue
let listeners: ((toasts: ToastMessage[]) => void)[] = [];
let toasts: ToastMessage[] = [];

function emitChange() {
  for (const listener of listeners) {
    listener(toasts);
  }
}

function generateId() {
  return Math.random().toString(36).substring(2, 9);
}

function addToast(toast: Omit<ToastMessage, "id">) {
  const id = generateId();
  toasts = [...toasts, { ...toast, id }];
  emitChange();

  if (toast.duration !== 0) {
    setTimeout(() => {
      removeToast(id);
    }, toast.duration || 4000);
  }
}

function removeToast(id: string) {
  toasts = toasts.filter((t) => t.id !== id);
  emitChange();
}

export function useToast() {
  const success = useCallback((title: string, message?: string, duration?: number) => {
    addToast({ type: "success", title, message, duration });
  }, []);

  const error = useCallback((title: string, message?: string, duration?: number) => {
    addToast({ type: "error", title, message, duration });
  }, []);

  const info = useCallback((title: string, message?: string, duration?: number) => {
    addToast({ type: "info", title, message, duration });
  }, []);

  const warning = useCallback((title: string, message?: string, duration?: number) => {
    addToast({ type: "warning", title, message, duration });
  }, []);

  return { success, error, info, warning };
}

// This component is mounted once by ToastProvider
export function ToastContainer() {
  const [currentToasts, setCurrentToasts] = useState<ToastMessage[]>(toasts);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    listeners.push(setCurrentToasts);
    return () => {
      listeners = listeners.filter((l) => l !== setCurrentToasts);
    };
  }, []);

  if (!mounted) return null;

  const el = document.getElementById("toast-container");
  if (!el) return null;

  return createPortal(
    <>
      {currentToasts.map((toast) => (
        <div
          key={toast.id}
          className="pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-lg bg-surface p-4 shadow-lg ring-1 ring-border animate-slide-in"
        >
          <div className="flex-shrink-0">
            {toast.type === "success" && <CheckIcon className="h-5 w-5 text-success" />}
            {toast.type === "error" && <AlertCircleIcon className="h-5 w-5 text-danger" />}
            {toast.type === "info" && <InfoIcon className="h-5 w-5 text-info" />}
            {toast.type === "warning" && <AlertTriangleIcon className="h-5 w-5 text-warning" />}
          </div>
          <div className="flex-1 pt-0.5">
            <p className="text-sm font-medium text-foreground">{toast.title}</p>
            {toast.message && <p className="mt-1 text-sm text-muted">{toast.message}</p>}
          </div>
          <div className="flex flex-shrink-0 ml-4">
            <button
              onClick={() => removeToast(toast.id)}
              className="inline-flex rounded-md bg-surface text-muted hover:text-foreground focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <span className="sr-only">Close</span>
              <CloseIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      ))}
    </>,
    el
  );
}
