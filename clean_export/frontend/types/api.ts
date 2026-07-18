/**
 * types/api.ts — Alias-only file.
 *
 * All types here are re-exported from generated/api.ts (produced by openapi-typescript).
 * This file is the only permitted import point for backend schema types.
 * Do NOT add handwritten type definitions here — add them to types/app.ts instead.
 *
 * To regenerate:
 *   npm run generate:api
 */

// NOTE: generated/api.ts is produced at build time.
// Until the first generation run, we declare the types manually below
// so the codebase compiles. Once generated/api.ts exists, replace these
// with re-exports: export type { ... } from "@/generated/api";

export interface CursorPage<T> {
  items: T[];
  next_cursor: string | null;
  has_more: boolean;
}

export interface ApiError {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
}

// SSE envelope
export interface SseEvent<T = unknown> {
  stream_id: string;
  id: string;
  event: string;
  data: T;
  retry?: number;
}

// SSE event payloads
export interface ConversationStartedEvent { conversation_id: string; }
export interface AssistantDeltaEvent      { text: string; }
export interface ToolStartedEvent         { tool_name: string; tool_id: string; }
export interface ToolProgressEvent        { tool_id: string; message: string; }
export interface ToolCompletedEvent       { tool_id: string; summary: string; }
export interface CitationEvent            { document_id: string; title: string; snippet: string; }
export interface ErrorEvent               { type: string; title: string; status: number; detail: string; instance?: string; }
export interface HeartbeatEvent           { [key: string]: never; }

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ConversationCompletedEvent {
  conversation_id: string;
  assistant_message_id: string;
  usage: TokenUsage;
  finish_reason: string;
  latency_ms: number;
  tool_count: number;
}

// Domain models
export interface User {
  id: string;
  email: string;
  name: string;
  roles: string[];
  workspace_id: string;
  permissions: string[];
}

export interface ConversationResponse {
  id: string;
  title: string | null;
  workspace_id: string | null;
  state: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationListResponse {
  items: ConversationResponse[];
  total: number;
}

export interface DashboardStats {
  total_documents: number;
  total_assets: number;
  active_conflicts: number;
  processing_jobs: number;
}

export interface RecentDocument {
  id: string;
  title: string;
  status: string;
  uploaded_at: string;
}

export interface ProcessingQueueItem {
  job_id: string;
  document_title: string;
  status: string;
  progress: number;
  started_at: string | null;
}

export interface DashboardOverviewResponse {
  stats: DashboardStats;
  recent_documents: RecentDocument[];
  processing_queue: ProcessingQueueItem[];
}

export interface AssetSummary {
  id: string;
  name: string;
  health_status: string;
  last_updated: string;
}

export interface AssetDetailResponse {
  id: string;
  name: string;
  description: string | null;
  metadata: Record<string, unknown>;
  health_status: string;
  processing_status: string;
  last_updated: string;
  document_count: number;
  last_processed: string | null;
  links: string[];
}

export interface FactSummary {
  id: string;
  property_name: string;
  value: string;
  confidence: number;
  source_document_id: string;
}

export interface FindingSummary {
  id: string;
  finding_type: string;
  description: string;
  severity: string;
  created_at: string;
}
