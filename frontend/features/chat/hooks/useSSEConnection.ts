import { useEffect, useRef, useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { SSEConnectionManager, type ConnectionState } from "../sse/SSEConnectionManager";
import { EventRouter } from "../sse/EventRouter";

export function useSSEConnection(conversationId: string | undefined) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<ConnectionState>("DISCONNECTED");
  const managerRef = useRef<SSEConnectionManager | null>(null);

  const connect = useCallback((cursor?: string) => {
    if (!conversationId) return;

    if (!managerRef.current) {
      const router = new EventRouter(queryClient, conversationId);
      
      managerRef.current = new SSEConnectionManager({
        url: `/chat/conversations/${conversationId}/stream`,
        onStateChange: (newState) => setState(newState),
        onEvent: (event) => router.routeEvent(event),
        onError: (err) => console.error("[useSSEConnection] Stream error:", err),
      });
    }

    managerRef.current.connect(cursor);
  }, [conversationId, queryClient]);

  const disconnect = useCallback(() => {
    managerRef.current?.disconnect();
    managerRef.current = null;
    setState("DISCONNECTED");
  }, []);

  const cancelStream = useCallback(() => {
    managerRef.current?.cancelStream();
  }, []);

  // Cleanup on unmount or conversation change
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    state,
    isStreaming: state === "CONNECTING" || state === "CONNECTED",
    connect,
    disconnect,
    cancelStream,
  };
}
