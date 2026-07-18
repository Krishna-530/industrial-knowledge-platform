export type SSEEventType =
  | "conversation_started"
  | "message_started"
  | "message_delta"
  | "message_completed"
  | "tool_started"
  | "tool_completed"
  | "citation_added"
  | "heartbeat"
  | "stream_error"
  | "stream_completed";

export interface SSEEvent<T = any> {
  type: SSEEventType;
  sequence: number;
  payload: T;
}

export interface MessageDeltaPayload {
  message_id: string;
  delta: string;
}

export interface MessageStartedPayload {
  message_id: string;
  conversation_id: string;
  role: "assistant";
}

export interface MessageCompletedPayload {
  message_id: string;
  reason: "stop" | "max_tokens" | "error";
}

export interface StreamErrorPayload {
  code: string;
  message: string;
}
