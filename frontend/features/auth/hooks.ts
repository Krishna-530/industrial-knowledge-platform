"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { authQueryKeys } from "./query";
import { authenticatedRequest } from "@/lib/network/auth-interceptor";
import { httpRequest } from "@/lib/network/http-client";
import { setAccessToken, clearAccessToken } from "@/lib/network/auth-token-store";
import type { User } from "@/types/api";
import type { LoginCredentials } from "@/types/app";

/**
 * useCurrentUser
 *
 * Retrieves the currently authenticated user from the React Query cache.
 * Components must use this hook instead of checking AuthContext.user.
 */
export function useCurrentUser() {
  return useQuery<User | null>({
    queryKey: authQueryKeys.me,
    queryFn: async () => {
      try {
        return await authenticatedRequest<User>({ path: "/users/me", method: "GET" });
      } catch {
        return null;
      }
    },
    // The user identity should not go stale quickly, but when we revisit the page,
    // we want to ensure we have the latest permissions if they changed.
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}


