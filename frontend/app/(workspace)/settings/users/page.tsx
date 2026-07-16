"use client";

import React, { useState } from "react";
import { Users, UserPlus } from "lucide-react";
import { useCurrentUser } from "@/features/auth/hooks";
import { useUsers, useRoles } from "@/features/users/hooks";
import { UserList } from "@/features/users/components/UserList";
import { CreateUserModal } from "@/features/users/components/CreateUserModal";
import { PermissionError, NetworkError } from "@/components/feedback/ErrorStates";
import { useQueryClient } from "@tanstack/react-query";
import { usersKeys, rolesKeys } from "@/lib/query-keys";

export default function UserManagementPage() {
  const [page, setPage] = useState(0);
  const limit = 10;
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const { data: currentUser, isLoading: isAuthLoading } = useCurrentUser();
  
  const { 
    data: usersData, 
    isLoading: isUsersLoading,
    isError: isUsersError 
  } = useUsers(limit, page * limit);
  
  const { 
    data: rolesData, 
    isLoading: isRolesLoading,
    isError: isRolesError 
  } = useRoles(100, 0);

  const queryClient = useQueryClient();

  const handleRetry = () => {
    queryClient.invalidateQueries({ queryKey: usersKeys.all });
    queryClient.invalidateQueries({ queryKey: rolesKeys.all });
  };

  if (isAuthLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Route Protection: Admin Only
  const isAdmin = currentUser?.roles?.includes("Admin");
  
  if (!isAdmin) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <PermissionError 
          title="Administrative Access Required" 
          message="You do not have permission to manage users and roles. Please contact an administrator." 
        />
      </div>
    );
  }

  if (isUsersError || isRolesError) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <NetworkError onRetry={handleRetry} />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div className="flex items-center text-gray-900 dark:text-gray-100">
          <Users className="w-8 h-8 mr-3 text-blue-600 dark:text-blue-500" />
          <div>
            <h1 className="text-2xl font-bold">User Management</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Provision accounts, assign roles, and manage access.
            </p>
          </div>
        </div>
        
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors shadow-sm text-sm font-medium"
          >
            <UserPlus className="w-4 h-4 mr-2" />
            Create User
          </button>
        </div>
      </div>

      <UserList 
        users={usersData?.items || []} 
        roles={rolesData?.items || []} 
        total={usersData?.total || 0}
        isLoading={isUsersLoading || isRolesLoading}
        page={page}
        setPage={setPage}
        limit={limit}
      />

      {isCreateModalOpen && (
        <CreateUserModal 
          roles={rolesData?.items || []} 
          onClose={() => setIsCreateModalOpen(false)} 
        />
      )}
    </div>
  );
}
