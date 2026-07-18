import { apiClient } from "@/lib/api-client";
import type { Conversation, Message, Role, ConversationLifecycle, MessageStatus } from "./types";

function mapConversation(raw: any): Conversation {
  return {
    id: String(raw.id),
    title: String(raw.title || "New Conversation"),
    lifecycle: (raw.lifecycle || "ACTIVE") as ConversationLifecycle,
    createdAt: String(raw.created_at || new Date().toISOString()),
    updatedAt: String(raw.updated_at || new Date().toISOString()),
    lastMessageAt: raw.last_message_at ? String(raw.last_message_at) : undefined,
  };
}

function mapMessage(raw: any): Message {
  return {
    id: String(raw.id),
    conversationId: String(raw.conversation_id),
    role: (raw.role || "user") as Role,
    content: String(raw.content || ""),
    status: (raw.status || "COMPLETED") as MessageStatus,
    createdAt: String(raw.created_at || new Date().toISOString()),
    updatedAt: String(raw.updated_at || new Date().toISOString()),
  };
}

export async function getConversations(page: number = 1, pageSize: number = 20) {
  const data = await apiClient<any>({
    endpoint: `/chat/conversations?page=${page}&page_size=${pageSize}`,
    method: "GET",
  });
  return {
    items: (data.items || []).map(mapConversation),
    total: data.total ?? 0,
    page: data.page ?? page,
    pageSize: data.page_size ?? pageSize,
    totalPages: data.total_pages ?? 1,
  };
}

export async function getConversationDetails(id: string): Promise<Conversation> {
  const data = await apiClient<any>({
    endpoint: `/chat/conversations/${id}`,
    method: "GET",
  });
  return mapConversation(data);
}

export async function getMessages(conversationId: string, page: number = 1, pageSize: number = 50) {
  const data = await apiClient<any>({
    endpoint: `/chat/conversations/${conversationId}/messages?page=${page}&page_size=${pageSize}`,
    method: "GET",
  });
  return {
    items: (data.items || []).map(mapMessage),
    total: data.total ?? 0,
    page: data.page ?? page,
    pageSize: data.page_size ?? pageSize,
    totalPages: data.total_pages ?? 1,
  };
}

export async function createConversation(): Promise<Conversation> {
  const data = await apiClient<any>({
    endpoint: `/chat/conversations`,
    method: "POST",
  });
  return mapConversation(data);
}

export async function deleteConversation(id: string): Promise<void> {
  await apiClient<void>({
    endpoint: `/chat/conversations/${id}`,
    method: "DELETE",
  });
}

// Additional mutation for Phase 11.2.4.1 testing, since we don't stream yet.
export async function sendMessage(conversationId: string, content: string): Promise<Message> {
  const data = await apiClient<any>({
    endpoint: `/chat/conversations/${conversationId}/messages`,
    method: "POST",
    body: JSON.stringify({ content }),
  });
  return mapMessage(data);
}
