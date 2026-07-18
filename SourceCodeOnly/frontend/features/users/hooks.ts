import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usersKeys, rolesKeys } from "@/lib/query-keys";
import { 
  listUsers, getUser, createUser, updateUser, activateUser, 
  deactivateUser, assignRole, resetPassword, listRoles, getRole 
} from "./api";
import type { 
  CreateUserRequest, UpdateUserRequest, UpdateRoleRequest, 
  UpdatePasswordRequest 
} from "./types";

// --- Users Hooks ---

export function useUsers(limit: number = 50, offset: number = 0) {
  return useQuery({
    queryKey: usersKeys.list({ limit, offset }),
    queryFn: () => listUsers(limit, offset),
    staleTime: 60 * 1000, // 1 minute
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: usersKeys.detail(id),
    queryFn: () => getUser(id),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateUserRequest) => createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: usersKeys.all });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateUserRequest }) => updateUser(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: usersKeys.lists() });
      queryClient.setQueryData(usersKeys.detail(data.id), data);
    },
  });
}

export function useActivateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => activateUser(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: usersKeys.lists() });
      queryClient.setQueryData(usersKeys.detail(data.id), data);
    },
  });
}

export function useDeactivateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => deactivateUser(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: usersKeys.lists() });
      queryClient.setQueryData(usersKeys.detail(data.id), data);
    },
  });
}

export function useAssignRole() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateRoleRequest }) => assignRole(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: usersKeys.lists() });
      queryClient.setQueryData(usersKeys.detail(data.id), data);
    },
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdatePasswordRequest }) => resetPassword(id, data),
  });
}

// --- Roles Hooks ---

export function useRoles(limit: number = 50, offset: number = 0) {
  return useQuery({
    queryKey: rolesKeys.list({ limit, offset }),
    queryFn: () => listRoles(limit, offset),
    staleTime: 5 * 60 * 1000, // Roles rarely change, 5 min stale
  });
}

export function useRole(id: string) {
  return useQuery({
    queryKey: rolesKeys.detail(id),
    queryFn: () => getRole(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}
