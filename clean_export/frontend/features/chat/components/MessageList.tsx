import React from "react";
import { MessageBubble } from "./MessageBubble";
import { CitationDrawer } from "./CitationDrawer";
import type { Message } from "../types";

export interface MessageListProps {
  messages: Message[];
  scrollContainerRef: React.RefObject<HTMLDivElement>;
}

export function MessageList({ messages, scrollContainerRef }: MessageListProps) {
  // Empty Conversation Contract:
  // "If a conversation exists but has 0 messages -> renders a welcome message and enables the input (no blank pages)."
  if (messages.length === 0) {
    return (
      <div 
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto p-4 sm:p-6 flex flex-col items-center justify-center text-center space-y-4"
      >
        <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-2xl flex items-center justify-center mb-2">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          Start a new conversation
        </h3>
        <p className="text-gray-500 dark:text-gray-400 max-w-sm">
          Ask questions about your assets, extract insights from documents, or analyze system conflicts.
        </p>
        <CitationDrawer />
      </div>
    );
  }

  return (
    <>
      <div 
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-2"
      >
        {messages.map((msg) => (
          <MessageBubble 
            key={msg.id} 
            message={msg} 
            status={msg.status} 
          />
        ))}
      </div>
      <CitationDrawer />
    </>
  );
}
