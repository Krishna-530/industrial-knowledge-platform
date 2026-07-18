import React, { useState } from "react";
import { 
  MoreVertical, Shield, Key, UserCheck, UserX, Trash2 
} from "lucide-react";
import type { User, Role } from "../types";
import { 
  useActivateUser, useDeactivateUser, useAssignRole, useResetPassword 
} from "../hooks";
import { useCurrentUser } from "@/features/auth/hooks";

interface UserActionsProps {
  user: User;
  roles: Role[];
}

export function UserActions({ user, roles }: UserActionsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [newPassword, setNewPassword] = useState("");
  const { data: currentUser } = useCurrentUser();
  
  const activateMutation = useActivateUser();
  const deactivateMutation = useDeactivateUser();
  const assignRoleMutation = useAssignRole();
  const resetPasswordMutation = useResetPassword();

  const isSelf = currentUser?.id === user.id;

  const handleActivate = async () => {
    await activateMutation.mutateAsync(user.id);
    setIsOpen(false);
  };

  const handleDeactivate = async () => {
    if (isSelf) {
      alert("You cannot deactivate your own account.");
      return;
    }
    await deactivateMutation.mutateAsync(user.id);
    setIsOpen(false);
  };

  const handleRoleChange = async (roleId: string) => {
    if (isSelf) {
      alert("You cannot change your own role.");
      return;
    }
    await assignRoleMutation.mutateAsync({ id: user.id, data: { role_id: roleId } });
    setIsOpen(false);
  };

  const handleResetPassword = async () => {
    if (newPassword.length < 8) {
      alert("Password must be at least 8 characters.");
      return;
    }
    await resetPasswordMutation.mutateAsync({ 
      id: user.id, 
      data: { password: newPassword } 
    });
    setIsResetting(false);
    setNewPassword("");
    setIsOpen(false);
    alert("Password reset successfully.");
  };

  return (
    <div className="relative inline-block text-left">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500"
      >
        <MoreVertical className="w-5 h-5" />
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => { setIsOpen(false); setIsResetting(false); }} 
          />
          <div className="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-gray-900 ring-1 ring-black ring-opacity-5 z-20 overflow-hidden divide-y divide-gray-100 dark:divide-gray-800">
            {isResetting ? (
              <div className="p-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  New Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-transparent text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
                  placeholder="Min 8 chars"
                />
                <div className="flex space-x-2">
                  <button
                    onClick={handleResetPassword}
                    className="flex-1 bg-blue-600 text-white text-xs py-1.5 rounded-md hover:bg-blue-700"
                  >
                    Reset
                  </button>
                  <button
                    onClick={() => setIsResetting(false)}
                    className="flex-1 bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs py-1.5 rounded-md hover:bg-gray-300 dark:hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="py-1">
                  {user.is_active ? (
                    <button
                      onClick={handleDeactivate}
                      disabled={isSelf || deactivateMutation.isPending}
                      className="w-full text-left px-4 py-2 text-sm text-amber-600 dark:text-amber-500 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <UserX className="w-4 h-4 mr-2" />
                      Deactivate User
                    </button>
                  ) : (
                    <button
                      onClick={handleActivate}
                      disabled={activateMutation.isPending}
                      className="w-full text-left px-4 py-2 text-sm text-emerald-600 dark:text-emerald-500 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center disabled:opacity-50"
                    >
                      <UserCheck className="w-4 h-4 mr-2" />
                      Activate User
                    </button>
                  )}
                  
                  <button
                    onClick={() => setIsResetting(true)}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center"
                  >
                    <Key className="w-4 h-4 mr-2 text-gray-400" />
                    Reset Password
                  </button>
                </div>
                
                <div className="py-1">
                  <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center">
                    <Shield className="w-3 h-3 mr-1" />
                    Change Role
                  </div>
                  {roles.map(role => (
                    <button
                      key={role.id}
                      onClick={() => handleRoleChange(role.id)}
                      disabled={isSelf || role.id === user.role_id || assignRoleMutation.isPending}
                      className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center ${
                        role.id === user.role_id 
                          ? "text-blue-600 dark:text-blue-400 bg-blue-50/50 dark:bg-blue-900/10" 
                          : "text-gray-700 dark:text-gray-300"
                      } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      {role.name}
                      {role.id === user.role_id && <span className="ml-auto text-xs">Current</span>}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
}
