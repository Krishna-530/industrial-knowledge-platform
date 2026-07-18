import React from "react";
import { User, Bot, AlertCircle } from "lucide-react";
import { MarkdownRenderer } from "./MarkdownRenderer";
import type { Message, MessageStatus } from "../types";

export interface MessageBubbleProps {
  message: Message;
  status: MessageStatus;
  attachments?: React.ReactNode;
  citations?: React.ReactNode;
  toolCards?: React.ReactNode;
}

const MessageBubbleContent = ({ message, status, attachments, citations, toolCards }: MessageBubbleProps) => {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";
  const isStreaming = status === "STREAMING";

  if (isSystem) {
    return (
      <div className="flex justify-center my-4">
        <span className="text-xs font-medium text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full">
          {message.content}
        </span>
      </div>
    );
  }

  return (
    <div className={`flex w-full mb-6 ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex max-w-[85%] ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        
        {/* Avatar */}
        <div className={`flex-shrink-0 flex items-start ${isUser ? "ml-3" : "mr-3"}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? "bg-blue-600 text-white" : "bg-emerald-600 text-white"
          }`}>
            {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
          </div>
        </div>

        {/* Message Body */}
        <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
          <div className={`px-4 py-3 rounded-2xl ${
            isUser 
              ? "bg-blue-600 text-white rounded-tr-sm" 
              : "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700 shadow-sm rounded-tl-sm"
          }`}>
            <div className="text-sm">
              {isUser ? (
                <p className="whitespace-pre-wrap">{message.content}</p>
              ) : (
                <div className="relative">
                  <MarkdownRenderer 
                    content={message.content} 
                    isStreaming={isStreaming} 
                  />
                  {isStreaming && (
                    <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse align-middle opacity-75" aria-hidden="true" />
                  )}
                </div>
              )}
            </div>
            
            {/* Future Attachments/Cards Slots */}
            {attachments && <div className="mt-3">{attachments}</div>}
            {toolCards && <div className="mt-3">{toolCards}</div>}
            {citations && <div className="mt-3">{citations}</div>}
          </div>

          {/* Status Indicators */}
          {(status === "PENDING" || status === "SENDING") && (
            <span className="text-xs text-gray-400 mt-1 mr-1 animate-pulse">Sending...</span>
          )}
          {status === "FAILED" && (
            <div className="flex items-center text-xs text-red-500 mt-1 mr-1">
              <AlertCircle className="w-3 h-3 mr-1" />
              Failed to send
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const MessageBubble = React.memo(MessageBubbleContent);
