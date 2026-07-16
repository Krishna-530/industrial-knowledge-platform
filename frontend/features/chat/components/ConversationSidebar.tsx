import React from "react";
import { MessageSquare, Plus, Edit2, Trash2, MoreVertical } from "lucide-react";
import type { Conversation } from "../types";

export interface ConversationSidebarProps {
  conversations: Conversation[];
  selectedConversationId: string | null;
  onSelect(id: string): void;
  onCreate(): void;
  onRename(id: string): void;
  onDelete(id: string): void;
}

export function ConversationSidebar({
  conversations,
  selectedConversationId,
  onSelect,
  onCreate,
  onRename,
  onDelete
}: ConversationSidebarProps) {
  
  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 w-full sm:w-64 flex-shrink-0">
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <button
          onClick={onCreate}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Plus className="w-4 h-4" />
          <span>New Chat</span>
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-sm text-gray-500 dark:text-gray-400">
            No conversations yet.
          </div>
        ) : (
          conversations.map((conv) => {
            const isSelected = selectedConversationId === conv.id;
            return (
              <div
                key={conv.id}
                className={`group relative flex items-center px-3 py-2 text-sm font-medium rounded-md cursor-pointer ${
                  isSelected
                    ? "bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white"
                    : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800/50"
                }`}
              >
                <div 
                  className="flex-1 flex items-center overflow-hidden" 
                  onClick={() => onSelect(conv.id)}
                >
                  <MessageSquare className={`flex-shrink-0 w-4 h-4 mr-3 ${isSelected ? "text-blue-600 dark:text-blue-400" : "text-gray-400"}`} />
                  <span className="truncate">{conv.title}</span>
                </div>
                
                {/* Actions */}
                <div className={`flex items-center ml-2 ${isSelected ? "opacity-100" : "opacity-0 group-hover:opacity-100"} transition-opacity`}>
                   <div className="relative group/menu">
                    <button 
                      className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
                      aria-label="Conversation Options"
                    >
                      <MoreVertical className="w-4 h-4" />
                    </button>
                    <div className="absolute right-0 mt-1 w-32 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 invisible group-hover/menu:visible z-30">
                      <div className="py-1">
                        <button
                          onClick={(e) => { e.stopPropagation(); onRename(conv.id); }}
                          className="w-full text-left px-4 py-2 text-xs text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                        >
                          <Edit2 className="w-3 h-3 mr-2" />
                          Rename
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); onDelete(conv.id); }}
                          className="w-full text-left px-4 py-2 text-xs text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center"
                        >
                          <Trash2 className="w-3 h-3 mr-2" />
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
