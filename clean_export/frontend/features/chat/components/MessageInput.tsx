import React, { useRef, useEffect, useState } from "react";
import { Send, Square } from "lucide-react";

export interface MessageInputProps {
  onSend(message: string): void;
  onStop?(): void;
  disabled: boolean;
  isStreaming: boolean;
  placeholder?: string;
  maxLength?: number;
}

export function MessageInput({ 
  onSend,
  onStop,
  disabled, 
  isStreaming, 
  placeholder = "Type your message...", 
  maxLength = 4000 
}: MessageInputProps) {
  const [content, setContent] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize logic
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [content]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && content.trim() && !isStreaming) {
        onSend(content.trim());
        setContent("");
      }
    }
  };

  const handleSend = () => {
    if (!disabled && content.trim() && !isStreaming) {
      onSend(content.trim());
      setContent("");
    }
  };

  const handleStop = () => {
    if (onStop) {
      onStop();
    }
  };

  const isSubmitDisabled = disabled || (!content.trim() && !isStreaming);

  return (
    <div className="relative rounded-lg shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-700 bg-white dark:bg-gray-900 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-600">
      <textarea
        ref={textareaRef}
        rows={1}
        name="message"
        id="message"
        disabled={disabled} // disables input during FAILED or read-only states
        className="block w-full resize-none border-0 bg-transparent py-3 pl-4 pr-12 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6 max-h-[200px]"
        placeholder={placeholder}
        maxLength={maxLength}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        autoFocus
      />
      
      <div className="absolute bottom-2 right-2 flex items-center">
        {isStreaming ? (
          <button
            type="button"
            onClick={handleStop}
            className="inline-flex items-center justify-center rounded-md bg-red-600 p-2 text-white hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
            aria-label="Stop generating"
          >
            <Square className="h-4 w-4" aria-hidden="true" fill="currentColor" />
          </button>
        ) : (
          <button
            type="button"
            disabled={isSubmitDisabled}
            onClick={handleSend}
            className="inline-flex items-center justify-center rounded-md bg-blue-600 p-2 text-white hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            aria-label="Send message"
          >
            <Send className="h-4 w-4" aria-hidden="true" />
          </button>
        )}
      </div>
    </div>
  );
}
