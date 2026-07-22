/**
 * features/documents/components/DemoUploadPanel.tsx
 *
 * Self-contained upload simulation panel for Demo Mode.
 * Shows a multi-step animated pipeline, generates realistic metadata,
 * then writes the new document into the demo store.
 *
 * This component is ONLY mounted when DEMO_MODE=true.
 * It is never imported by production document list pages directly —
 * the EmptyDocuments component conditionally renders it via feature-flag check.
 */

"use client";

import React, { useCallback, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Upload, CheckCircle2, AlertCircle, FileText, X } from "lucide-react";
import { demoStore } from "@/lib/demo/demoStore";
import { UPLOAD_PIPELINE_STEPS } from "@/lib/demo/demoKnowledgeBase";
import { randomDuration } from "@/lib/demo/intentMatcher";
import { documentKeys, dashboardKeys } from "@/lib/query-keys";
import type { DemoDocument } from "@/lib/demo/types";
import type { UploadStep, UploadStage } from "@/lib/demo/types";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function generatePageCount(): number {
  const choices = [14, 23, 38, 54, 67, 89, 102, 118, 134, 159, 176, 203, 243];
  return choices[Math.floor(Math.random() * choices.length)];
}

function generateChunkCount(pages: number): number {
  return Math.floor(pages * 1.8 + Math.random() * pages * 0.4);
}

function generateEntityCount(pages: number): number {
  return Math.floor(pages * 0.42 + Math.random() * pages * 0.15);
}

function generateRelationshipCount(entities: number): number {
  return Math.floor(entities * 2.1 + Math.random() * entities * 0.5);
}

function generateFileSize(): number {
  // Between 800KB and 12MB
  return Math.floor(800_000 + Math.random() * 11_200_000);
}

// ─── Component ────────────────────────────────────────────────────────────────

interface DemoUploadPanelProps {
  onClose?: () => void;
}

type StepStatus = "pending" | "active" | "done";

interface StepState {
  step: UploadStep;
  status: StepStatus;
}

export function DemoUploadPanel({ onClose }: DemoUploadPanelProps) {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [stage, setStage] = useState<UploadStage>("idle");
  const [filename, setFilename] = useState<string>("");
  const [steps, setSteps] = useState<StepState[]>([]);
  const [completedDoc, setCompletedDoc] = useState<DemoDocument | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runSimulation = useCallback(async (file: File) => {
    setFilename(file.name);
    setStage("in_progress");
    setError(null);
    setCompletedDoc(null);

    const stepStates: StepState[] = UPLOAD_PIPELINE_STEPS.map(s => ({ step: s, status: "pending" as StepStatus }));
    setSteps([...stepStates]);

    // Run each step sequentially with randomized duration
    for (let i = 0; i < stepStates.length; i++) {
      stepStates[i] = { ...stepStates[i], status: "active" };
      setSteps([...stepStates]);

      await new Promise(r => setTimeout(r, randomDuration(stepStates[i].step.durationRange)));

      stepStates[i] = { ...stepStates[i], status: "done" };
      setSteps([...stepStates]);
    }

    // Generate realistic metadata
    const pageCount         = generatePageCount();
    const chunkCount        = generateChunkCount(pageCount);
    const entityCount       = generateEntityCount(pageCount);
    const relationshipCount = generateRelationshipCount(entityCount);

    const doc: DemoDocument = {
      id:               `doc-uploaded-${Date.now()}`,
      filename:         file.name,
      title:            file.name.replace(/\.[^.]+$/, ""),
      status:           "active",
      uploadedAt:       new Date().toISOString(),
      pageCount,
      chunkCount,
      entityCount,
      relationshipCount,
      mimeType:         file.type || "application/pdf",
      fileSize:         file.size || generateFileSize(),
    };

    // Persist to demo store
    demoStore.addDocument(doc);
    setCompletedDoc(doc);
    setStage("completed");

    // Invalidate React Query caches so document list and dashboard update immediately
    queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    queryClient.invalidateQueries({ queryKey: dashboardKeys.all });
  }, [queryClient]);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    runSimulation(file);
  }, [runSimulation]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (!file) return;
    runSimulation(file);
  }, [runSimulation]);

  const handleReset = () => {
    setStage("idle");
    setSteps([]);
    setCompletedDoc(null);
    setFilename("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="relative bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <Upload className="w-5 h-5 text-blue-500" />
          <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">Upload Document</h2>
        </div>
        {onClose && (
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="p-6 space-y-5">
        {/* Drop Zone — shown when idle or after completion */}
        {(stage === "idle" || stage === "completed") && (
          <label
            htmlFor="demo-upload-input"
            onDragOver={e => e.preventDefault()}
            onDrop={handleDrop}
            className="flex flex-col items-center justify-center gap-3 w-full min-h-[160px] border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/20 transition-all duration-200"
          >
            <FileText className="w-10 h-10 text-gray-400 dark:text-gray-500" />
            <div className="text-center">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Drop a PDF here or <span className="text-blue-500 underline underline-offset-2">browse</span>
              </p>
              <p className="text-xs text-gray-400 mt-1">PDF, DOCX, PPTX up to 50MB</p>
            </div>
            <input
              id="demo-upload-input"
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.pptx,.doc"
              className="sr-only"
              onChange={handleFileChange}
            />
          </label>
        )}

        {/* Pipeline Steps — shown during and after upload */}
        {(stage === "in_progress" || stage === "completed") && steps.length > 0 && (
          <div className="space-y-1">
            {filename && (
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-3 truncate">
                Processing: <span className="text-gray-800 dark:text-gray-200">{filename}</span>
              </p>
            )}
            {steps.map((s, i) => (
              <div
                key={i}
                className="flex items-center gap-3 py-1.5 px-3 rounded-md transition-all duration-300"
                style={{ opacity: s.status === "pending" ? 0.35 : 1 }}
              >
                <span className="flex-shrink-0 w-5 h-5 flex items-center justify-center">
                  {s.status === "done" ? (
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                  ) : s.status === "active" ? (
                    <span className="w-3 h-3 rounded-full bg-blue-500 animate-pulse" />
                  ) : (
                    <span className="w-3 h-3 rounded-full border border-gray-300 dark:border-gray-600" />
                  )}
                </span>
                <span className={`text-sm ${s.status === "active" ? "font-medium text-blue-600 dark:text-blue-400" : s.status === "done" ? "text-gray-700 dark:text-gray-300" : "text-gray-400 dark:text-gray-600"}`}>
                  {s.step.label}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Completion Summary */}
        {stage === "completed" && completedDoc && (
          <div className="border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/20 rounded-lg p-4 space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <span className="text-sm font-semibold text-green-800 dark:text-green-300">
                Processing Complete
              </span>
            </div>
            <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs text-gray-600 dark:text-gray-400 mt-2">
              <span>Pages extracted</span>
              <span className="font-medium text-gray-800 dark:text-gray-200">{completedDoc.pageCount}</span>
              <span>Chunks indexed</span>
              <span className="font-medium text-gray-800 dark:text-gray-200">{completedDoc.chunkCount}</span>
              <span>Entities extracted</span>
              <span className="font-medium text-gray-800 dark:text-gray-200">{completedDoc.entityCount}</span>
              <span>Relationships created</span>
              <span className="font-medium text-gray-800 dark:text-gray-200">{completedDoc.relationshipCount}</span>
            </div>
            <button
              onClick={handleReset}
              className="mt-3 text-xs text-blue-500 hover:text-blue-700 font-medium transition-colors"
            >
              Upload another document
            </button>
          </div>
        )}

        {/* Error State */}
        {stage === "error" && (
          <div className="flex items-start gap-2 text-red-600 text-sm">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
}
