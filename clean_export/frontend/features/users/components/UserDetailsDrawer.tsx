import React from "react";
import { X, User as UserIcon, Shield, Clock, Calendar, Mail, CheckCircle, XCircle } from "lucide-react";
import type { User, Role } from "../types";

interface UserDetailsDrawerProps {
  user: User;
  roles: Role[];
  onClose: () => void;
}

export function UserDetailsDrawer({ user, roles, onClose }: UserDetailsDrawerProps) {
  const role = roles.find(r => r.id === user.role_id);

  const formatDate = (dateString: string) => {
    return new Intl.DateTimeFormat('en-US', {
      dateStyle: 'medium',
      timeStyle: 'short'
    }).format(new Date(dateString));
  };

  return (
    <>
      <div 
        className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-40 transition-opacity"
        onClick={onClose}
      />
      
      <div className="fixed inset-y-0 right-0 w-full max-w-md bg-white dark:bg-gray-900 shadow-xl z-50 transform transition-transform duration-300 flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-800">
          <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100 flex items-center">
            <UserIcon className="w-5 h-5 mr-2 text-gray-400" />
            User Profile
          </h2>
          <button 
            onClick={onClose}
            className="p-2 -mr-2 text-gray-400 hover:text-gray-500 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          <div className="px-6 py-8">
            <div className="flex items-center space-x-4 mb-8">
              <div className="h-16 w-16 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center text-2xl font-semibold">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">{user.name}</h3>
                <div className="flex items-center mt-1 space-x-2 text-sm text-gray-500 dark:text-gray-400">
                  <Mail className="w-4 h-4" />
                  <span>{user.email}</span>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wider">
                  Status & Role
                </h4>
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 space-y-4 border border-gray-100 dark:border-gray-800">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                      <Shield className="w-4 h-4 mr-2 text-gray-400" />
                      Role
                    </div>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400">
                      {role?.name || "Unknown"}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                      {user.is_active ? (
                        <CheckCircle className="w-4 h-4 mr-2 text-emerald-500" />
                      ) : (
                        <XCircle className="w-4 h-4 mr-2 text-red-500" />
                      )}
                      Status
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.is_active 
                        ? "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-400" 
                        : "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400"
                    }`}>
                      {user.is_active ? "Active" : "Inactive"}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wider">
                  Activity
                </h4>
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 space-y-4 border border-gray-100 dark:border-gray-800">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                      <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                      Created
                    </div>
                    <span className="text-sm text-gray-900 dark:text-gray-100">
                      {formatDate(user.created_at)}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                      <Clock className="w-4 h-4 mr-2 text-gray-400" />
                      Last Updated
                    </div>
                    <span className="text-sm text-gray-900 dark:text-gray-100">
                      {formatDate(user.updated_at)}
                    </span>
                  </div>
                </div>
              </div>

              {role && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wider">
                    Permissions
                  </h4>
                  <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 border border-gray-100 dark:border-gray-800">
                    {role.permissions.length > 0 ? (
                      <ul className="space-y-2">
                        {role.permissions.map(p => (
                          <li key={p.id} className="text-sm text-gray-700 dark:text-gray-300 flex items-start">
                            <CheckCircle className="w-4 h-4 mr-2 mt-0.5 text-blue-500 flex-shrink-0" />
                            <div>
                              <span className="font-medium block">{p.name}</span>
                              {p.description && <span className="text-xs text-gray-500">{p.description}</span>}
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <span className="text-sm text-gray-500">No specific permissions granted.</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
