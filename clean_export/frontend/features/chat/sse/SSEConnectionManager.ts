import { generateRequestId, X_REQUEST_ID_HEADER } from "@/lib/network/request-id";
import { EventParser } from "./EventParser";
import type { SSEEvent } from "./types";

export type ConnectionState = "CONNECTING" | "CONNECTED" | "DISCONNECTED" | "ERROR";

export interface SSEConnectionManagerOptions {
  url: string;
  onEvent: (event: SSEEvent) => void;
  onStateChange: (state: ConnectionState) => void;
  onError?: (error: Error) => void;
}

export class SSEConnectionManager {
  private abortController: AbortController | null = null;
  private state: ConnectionState = "DISCONNECTED";
  private retryCount = 0;
  private readonly MAX_RETRIES = 3;
  private heartbeatTimeoutId: NodeJS.Timeout | null = null;
  private reconnectTimeoutId: NodeJS.Timeout | null = null;
  
  constructor(private options: SSEConnectionManagerOptions) {}

  private setState(newState: ConnectionState) {
    if (this.state !== newState) {
      this.state = newState;
      this.options.onStateChange(newState);
    }
  }

  private resetHeartbeat() {
    if (this.heartbeatTimeoutId) clearTimeout(this.heartbeatTimeoutId);
    // If no events (including heartbeats) are received for 15 seconds, consider connection dead
    this.heartbeatTimeoutId = setTimeout(() => {
      console.warn("[SSE] Heartbeat timeout. Forcing reconnect...");
      this.handleDrop();
    }, 15_000);
  }

  public async connect(cursor?: string) {
    if (this.state === "CONNECTING" || this.state === "CONNECTED") return;
    
    this.setState("CONNECTING");
    this.abortController = new AbortController();
    
    try {
      // NOTE: In Phase 11.2.4.2.1 we simulate building the transport. 
      // Architecture contract dictates we use fetch to pass the token and X-Request-ID.
      // We read from the same process.env variable as the rest of the app.
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "";
      const endpoint = cursor 
        ? `${this.options.url}?cursor=${encodeURIComponent(cursor)}` 
        : this.options.url;

      const response = await fetch(`${baseUrl}${endpoint}`, {
        method: "GET",
        headers: {
          "Accept": "text/event-stream",
          [X_REQUEST_ID_HEADER]: generateRequestId(),
          // Authorization injected by interceptor or next-auth in real app, but for now we rely on cookies or passing token
        },
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`Failed to connect to stream: ${response.statusText}`);
      }
      
      this.setState("CONNECTED");
      this.retryCount = 0;
      this.resetHeartbeat();

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        this.resetHeartbeat();
        buffer += decoder.decode(value, { stream: true });
        
        // SSE lines are separated by \n\n
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() || ""; // Keep the incomplete chunk in buffer

        for (const chunk of chunks) {
          const trimmed = chunk.trim();
          if (!trimmed) continue;

          // Strip "data: " prefix standard in SSE
          const dataLine = trimmed.split("\n").find(line => line.startsWith("data: "));
          const rawData = dataLine ? dataLine.replace(/^data:\s*/, "") : trimmed;

          const event = EventParser.parseEvent(rawData);
          if (event) {
            this.options.onEvent(event);
          }
        }
      }

      // Stream closed gracefully by backend
      this.disconnect();
      
    } catch (error: any) {
      if (error.name === "AbortError") {
        console.log("[SSE] Stream aborted by client");
        this.disconnect();
      } else {
        console.error("[SSE] Stream error:", error);
        this.handleDrop(error);
      }
    }
  }

  private handleDrop(error?: Error) {
    this.disconnect();
    
    if (error && this.options.onError) {
      this.options.onError(error);
    }
    
    if (this.retryCount < this.MAX_RETRIES) {
      const backoffDelay = Math.pow(2, this.retryCount) * 1000; // 1s, 2s, 4s
      this.retryCount++;
      console.log(`[SSE] Reconnecting in ${backoffDelay}ms (Attempt ${this.retryCount}/${this.MAX_RETRIES})...`);
      this.reconnectTimeoutId = setTimeout(() => this.connect(), backoffDelay);
    } else {
      console.error("[SSE] Max retries reached. Stream failed.");
      this.setState("ERROR");
    }
  }

  public disconnect() {
    this.setState("DISCONNECTED");
    if (this.heartbeatTimeoutId) clearTimeout(this.heartbeatTimeoutId);
    if (this.reconnectTimeoutId) clearTimeout(this.reconnectTimeoutId);
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }

  public cancelStream() {
    console.log("[SSE] cancelStream called");
    this.disconnect();
  }
}
