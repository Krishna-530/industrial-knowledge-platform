export type Role = "user" | "assistant" | "system";

export type ConversationLifecycle =
  | "CREATED"
  | "ACTIVE"
  | "WAITING_FOR_RESPONSE"
  | "STREAMING"
  | "COMPLETED"
  | "FAILED";

export type MessageStatus =
  | "PENDING"
  | "SENDING"
  | "STREAMING"
  | "COMPLETED"
  | "FAILED";

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  lastMessageAt?: string;
  lifecycle: ConversationLifecycle; // Internal frontend abstraction of status if needed, though mostly derived or managed. Actually backend might not send this, but we explicitly defined it in types.
}

export interface Message {
  id: string;
  conversationId: string;
  role: Role;
  content: string; // Plain string for Phase 11.2.4.1
  status: MessageStatus;
  createdAt: string;
  updatedAt: string;
}
