import { QueryClient } from "@tanstack/react-query";
import { chatKeys } from "@/lib/query-keys";
import type { 
  SSEEvent, 
  MessageDeltaPayload, 
  MessageStartedPayload, 
  MessageCompletedPayload 
} from "./types";
import type { Message } from "../types";

export class EventRouter {
  private highestSequence = -1;
  private buffer = new Map<number, SSEEvent>();

  constructor(
    private queryClient: QueryClient,
    private conversationId: string
  ) {}

  public routeEvent(event: SSEEvent) {
    if (event.sequence <= this.highestSequence) {
      console.warn(`[EventRouter] Dropping duplicate or stale event seq: ${event.sequence}`);
      return;
    }

    if (event.sequence === this.highestSequence + 1) {
      // It's the exact next event we expect
      this.processEvent(event);
      this.highestSequence = event.sequence;
      this.flushBuffer();
    } else {
      // Out of order event (future)
      console.log(`[EventRouter] Buffering out-of-order event seq: ${event.sequence}`);
      this.buffer.set(event.sequence, event);
    }
  }

  private flushBuffer() {
    let nextSeq = this.highestSequence + 1;
    while (this.buffer.has(nextSeq)) {
      const bufferedEvent = this.buffer.get(nextSeq)!;
      this.processEvent(bufferedEvent);
      this.buffer.delete(nextSeq);
      this.highestSequence = nextSeq;
      nextSeq++;
    }
  }

  private processEvent(event: SSEEvent) {
    switch (event.type) {
      case "message_started":
        this.handleMessageStarted(event.payload as MessageStartedPayload);
        break;
      case "message_delta":
        this.handleMessageDelta(event.payload as MessageDeltaPayload);
        break;
      case "message_completed":
        this.handleMessageCompleted(event.payload as MessageCompletedPayload);
        break;
      case "stream_error":
        console.error("[EventRouter] Stream error received:", event.payload);
        break;
      // Other events silently ignored for Phase 11.2.4.2.1
    }
  }

  private handleMessageStarted(payload: MessageStartedPayload) {
    const queryKey = [...chatKeys.messages(this.conversationId), 1];
    
    this.queryClient.setQueryData(queryKey, (old: any) => {
      if (!old) return old;
      
      const newMessage: Message = {
        id: payload.message_id,
        conversationId: payload.conversation_id,
        role: payload.role,
        content: "",
        status: "STREAMING",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      return {
        ...old,
        items: [...old.items, newMessage],
        total: old.total + 1,
      };
    });
  }

  private handleMessageDelta(payload: MessageDeltaPayload) {
    const queryKey = [...chatKeys.messages(this.conversationId), 1];

    this.queryClient.setQueryData(queryKey, (old: any) => {
      if (!old) return old;

      return {
        ...old,
        items: old.items.map((msg: Message) => 
          msg.id === payload.message_id 
            ? { ...msg, content: msg.content + payload.delta, status: "STREAMING" }
            : msg
        ),
      };
    });
  }

  private handleMessageCompleted(payload: MessageCompletedPayload) {
    const queryKey = [...chatKeys.messages(this.conversationId), 1];

    this.queryClient.setQueryData(queryKey, (old: any) => {
      if (!old) return old;

      return {
        ...old,
        items: old.items.map((msg: Message) => 
          msg.id === payload.message_id 
            ? { ...msg, status: payload.reason === "error" ? "FAILED" : "COMPLETED" }
            : msg
        ),
      };
    });
  }
}
