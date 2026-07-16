export interface Permission {
  id: string;
  name: string;
  description?: string;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  is_system: boolean;
  created_at: string;
  updated_at: string;
  permissions: Permission[];
}

export interface RoleListResponse {
  items: Role[];
  total: number;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserListResponse {
  items: User[];
  total: number;
}

export interface CreateUserRequest {
  name: string;
  email: string;
  password: string;
  role_id: string;
}

export interface UpdateUserRequest {
  name?: string;
  email?: string;
}

export interface UpdatePasswordRequest {
  password: string;
}

export interface UpdateRoleRequest {
  role_id: string;
}
