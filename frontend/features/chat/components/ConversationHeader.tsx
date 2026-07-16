import React from "react";
import { MoreVertical, Edit2, Trash2 } from "lucide-react";

export interface ConversationHeaderProps {
  title: string;
  onRename?: () => void;
  onDelete?: () => void;
  statusIndicator?: React.ReactNode;
}

export function ConversationHeader({ title, onRename, onDelete, statusIndicator }: ConversationHeaderProps) {
  return (
    <div className="sticky top-0 z-10 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-4 py-3 sm:px-6">
      <div className="flex flex-col">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 truncate max-w-[200px] sm:max-w-md">
          {title}
        </h2>
        {statusIndicator && (
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            {statusIndicator}
          </div>
        )}
      </div>

      <div className="flex items-center space-x-2">
        <div className="relative group">
          <button 
            type="button"
            className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <MoreVertical className="w-5 h-5" />
          </button>
          
          {/* Simple Dropdown for actions */}
          <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 invisible group-hover:visible group-focus-within:visible z-20">
            <div className="py-1">
              {onRename && (
                <button
                  onClick={onRename}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                >
                  <Edit2 className="w-4 h-4 mr-2" />
                  Rename
                </button>
              )}
              {onDelete && (
                <button
                  onClick={onDelete}
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
