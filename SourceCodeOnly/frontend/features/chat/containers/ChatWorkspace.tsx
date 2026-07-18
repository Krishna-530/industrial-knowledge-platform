"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { 
  useConversations, 
  useConversation, 
  useMessages, 
  useCreateConversation, 
  useDeleteConversation, 
  useSendMessage 
} from "../hooks";
import { useSSEConnection } from "../hooks/useSSEConnection";
import { useAutoScroll } from "../hooks/useAutoScroll";
import { ConversationSidebar } from "../components/ConversationSidebar";
import { ConversationHeader } from "../components/ConversationHeader";
import { MessageList } from "../components/MessageList";
import { MessageInput } from "../components/MessageInput";
import { CitationDrawerProvider } from "../hooks/useCitation";
import { StreamErrorBoundary } from "../components/StreamErrorBoundary";
import { ConversationSidebarSkeleton } from "../components/ConversationSidebarSkeleton";
import { MessageListSkeleton } from "../components/MessageListSkeleton";
import { WelcomeScreen } from "../components/WelcomeScreen";
import { NetworkError } from "@/components/feedback/ErrorStates";
import { useToast } from "@/hooks/useToast";
import type { ConversationLifecycle } from "../types";

export interface ChatWorkspaceProps {
  conversationId?: string; // Present if loaded from /chat/[id], undefined if on /chat
}

export function ChatWorkspace({ conversationId }: ChatWorkspaceProps) {
  const router = useRouter();
  const toast = useToast();
  
  // Mobile drawer state
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Queries
  const conversationsQuery = useConversations(1); // List view (page 1)
  const conversationDetailsQuery = useConversation(conversationId || "");
  const messagesQuery = useMessages(conversationId || "", 1); // Phase 11.2.4.1 loads page 1

  // Mutations
  const createMutation = useCreateConversation();
  const deleteMutation = useDeleteConversation();
  const sendMessageMutation = useSendMessage();

  // SSE Connection removed since we stream directly on message send via the mutation.
  
  // Connect when a conversation is active
  React.useEffect(() => {
    // Left empty for structural parity
  }, [conversationId]);

  // Scroll Policy
  // We trigger auto-scroll whenever the messages array length changes.
  const messages = messagesQuery.data?.items || [];
  const { containerRef, scrollToBottom } = useAutoScroll<HTMLDivElement>([messages.length]);

  // Derived state & Lifecycles
  const activeConversation = conversationDetailsQuery.data;
  const lifecycle: ConversationLifecycle = activeConversation?.lifecycle || "ACTIVE";
  
  const isStreaming = lifecycle === "STREAMING" || lifecycle === "WAITING_FOR_RESPONSE" || sendMessageMutation.isPending;
  const isFailed = lifecycle === "FAILED";

  // Handlers
  const handleSelectConversation = (id: string) => {
    setIsSidebarOpen(false); // Mobile drawer rule
    router.push(`/chat/${id}`);
  };

  const handleCreateConversation = async () => {
    try {
      const newConv = await createMutation.mutateAsync();
      router.push(`/chat/${newConv.id}`);
    } catch (error) {
      toast.error("Failed to create conversation");
    }
  };

  const handleDeleteConversation = async (id: string) => {
    if (window.confirm("Delete this conversation?")) {
      try {
        await deleteMutation.mutateAsync(id);
        if (id === conversationId) {
          router.push("/chat");
        }
        toast.success("Conversation deleted");
      } catch (error) {
        toast.error("Failed to delete conversation");
      }
    }
  };

  const handleRenameConversation = (id: string) => {
    // Phase 11.2.4.1 placeholder
    toast.info("Rename coming in future phase");
  };

  const handleSendMessage = async (content: string) => {
    if (!conversationId) return;
    try {
      await sendMessageMutation.mutateAsync({ conversationId, content });
      scrollToBottom("smooth"); // Force scroll on optimistic update
    } catch (error) {
      toast.error("Failed to send message");
    }
  };

  // Render Sidebar
  const renderSidebar = () => {
    if (conversationsQuery.isLoading) return <ConversationSidebarSkeleton />;
    if (conversationsQuery.isError) return <div className="p-4 text-red-500">Failed to load history</div>;
    
    return (
      <ConversationSidebar
        conversations={conversationsQuery.data?.items || []}
        selectedConversationId={conversationId || null}
        onSelect={handleSelectConversation}
        onCreate={handleCreateConversation}
        onRename={handleRenameConversation}
        onDelete={handleDeleteConversation}
      />
    );
  };

  // Render Main Panel
  const renderPanel = () => {
    if (!conversationId) {
      return <WelcomeScreen onStartConversation={handleCreateConversation} />;
    }

    if (conversationDetailsQuery.isLoading || messagesQuery.isLoading) {
      return <MessageListSkeleton />;
    }

    if (conversationDetailsQuery.isError || messagesQuery.isError) {
      return <NetworkError onRetry={() => {
        conversationDetailsQuery.refetch();
        messagesQuery.refetch();
      }} />;
    }

    return (
      <div className="flex-1 flex flex-col min-w-0 bg-white dark:bg-gray-950">
        <ConversationHeader 
          title={activeConversation?.title || "Conversation"} 
          onRename={() => handleRenameConversation(conversationId)}
          onDelete={() => handleDeleteConversation(conversationId)}
          statusIndicator={
            isStreaming ? "Assistant is thinking..." : 
            isFailed ? "Conversation failed" : null
          }
        />
        
        <StreamErrorBoundary>
          <MessageList 
            messages={messages} 
            scrollContainerRef={containerRef} 
          />
        </StreamErrorBoundary>

        {/* Future Stream Placeholder */}
        {/* <StreamPlaceholder /> */}

        <div className="p-4 sm:p-6 bg-white dark:bg-gray-950">
          <div className="max-w-4xl mx-auto">
            <MessageInput 
              onSend={handleSendMessage}
              onStop={() => { /* Placeholder for abort controller cancellation */ }}
              disabled={isFailed || sendMessageMutation.isPending}
              isStreaming={isStreaming}
            />
            <div className="text-center mt-2">
              <span className="text-xs text-gray-400">AI can make mistakes. Verify important information.</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <CitationDrawerProvider>
      <div className="flex h-[calc(100vh-4rem)] overflow-hidden w-full relative">
        {/* Mobile Sidebar Overlay */}
        {isSidebarOpen && (
          <div 
            className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 sm:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}

        {/* Sidebar Container (Hidden on mobile unless open) */}
        <div className={`
          ${isSidebarOpen ? "fixed inset-y-0 left-0 z-50 flex" : "hidden"} 
          sm:static sm:flex h-full
        `}>
          {renderSidebar()}
        </div>

        {/* Main Chat Panel */}
        <div className="flex-1 flex flex-col min-w-0 relative">
          {/* Mobile Toggle Button (Visible only on small screens) */}
          <div className="sm:hidden absolute top-3 left-4 z-20">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 -ml-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white bg-white/50 dark:bg-gray-900/50 rounded-md backdrop-blur-sm"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
          
          {renderPanel()}
        </div>
      </div>
    </CitationDrawerProvider>
  );
}
