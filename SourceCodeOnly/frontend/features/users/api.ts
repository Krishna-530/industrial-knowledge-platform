import { apiClient } from "@/lib/api-client";
import type { 
  UserListResponse, User, CreateUserRequest, UpdateUserRequest, 
  UpdateRoleRequest, UpdatePasswordRequest, RoleListResponse, Role 
} from "./types";

// --- Users Router ---

export async function listUsers(limit: number = 50, offset: number = 0): Promise<UserListResponse> {
  return await apiClient<UserListResponse>({
    endpoint: `/users?limit=${limit}&offset=${offset}`,
    method: "GET",
  });
}

export async function getUser(id: string): Promise<User> {
  return await apiClient<User>({
    endpoint: `/users/${id}`,
    method: "GET",
  });
}

export async function createUser(data: CreateUserRequest): Promise<User> {
  return await apiClient<User>({
    endpoint: `/users`,
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateUser(id: string, data: UpdateUserRequest): Promise<User> {
  return await apiClient<User>({
    endpoint: `/users/${id}`,
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function activateUser(id: string): Promise<User> {
  return await apiClient<User>({
    endpoint: `/users/${id}/activate`,
    method: "PATCH",
  });
}

export async function deactivateUser(id: string): Promise<User> {
  return await apiClient<User>({
    endpoint: `/users/${id}/deactivate`,
    method: "PATCH",
  });
}

export async function assignRole(id: string, data: UpdateRoleRequest): Promise<User> {
  return await apiClient<User>({
    endpoint: `/users/${id}/role`,
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function resetPassword(id: string, data: UpdatePasswordRequest): Promise<User> {
  return await apiClient<User>({
    endpoint: `/users/${id}/password`,
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteUser(id: string): Promise<void> {
  await apiClient<void>({
    endpoint: `/users/${id}`,
    method: "DELETE",
  });
}

// --- Roles Router ---

export async function listRoles(limit: number = 50, offset: number = 0): Promise<RoleListResponse> {
  return await apiClient<RoleListResponse>({
    endpoint: `/roles?limit=${limit}&offset=${offset}`,
    method: "GET",
  });
}

export async function getRole(id: string): Promise<Role> {
  return await apiClient<Role>({
    endpoint: `/roles/${id}`,
    method: "GET",
  });
}
