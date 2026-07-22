/**
 * types/app.ts — Frontend-only types.
 *
 * These types are NOT derived from the backend OpenAPI spec.
 * They describe frontend state shapes, context interfaces, and UI contracts.
 */

import type { User } from "@/types/api";

// ─── Theme ───────────────────────────────────────────────────────────────────

export type ThemeMode = "light" | "dark" | "system";

export type ResolvedTheme = "light" | "dark";

export interface ThemeContextValue {
  mode: ThemeMode;
  resolvedTheme: ResolvedTheme;
  setMode: (mode: ThemeMode) => void;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export type AuthStatus =
  | "initializing"
  | "restoring"
  | "hydrating"
  | "authenticated"
  | "refreshing"
  | "authenticating"
  | "unauthenticated";

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthContextValue {
  status: AuthStatus;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
}

// ─── Navigation ───────────────────────────────────────────────────────────────

import type { Permission } from "@/lib/auth/permissions";

export interface NavItem {
  title: string;
  href: string;
  iconName: string;       // Key into the icon registry
  permission?: Permission; // If set, item hidden when user lacks this permission
  featureFlag?: string;   // If set, item hidden when feature flag is disabled
}

// ─── Feature Flags ────────────────────────────────────────────────────────────

export interface FeatureFlags {
  ENABLE_GRAPH_VIEW: boolean;
  ENABLE_ANALYTICS: boolean;
  ENABLE_MULTI_AGENT: boolean;
  ENABLE_KNOWLEDGE_GRAPH: boolean;
  ENABLE_EXPERIMENTAL_CHAT: boolean;
  DEMO_MODE: boolean;
}
