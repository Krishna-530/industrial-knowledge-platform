import type { SSEEvent } from "./types";

export class EventParser {
  /**
   * Safely parses a raw SSE string chunk into an SSEEvent DTO.
   * Returns null if the chunk is malformed or empty, protecting the router.
   */
  static parseEvent(raw: string): SSEEvent | null {
    if (!raw || !raw.trim()) {
      return null;
    }

    try {
      const parsed = JSON.parse(raw);
      
      // Basic validation of the event structure
      if (!parsed.type || typeof parsed.sequence !== "number") {
        console.warn("[EventParser] Dropped malformed event (missing type or sequence):", raw);
        return null;
      }
      
      return parsed as SSEEvent;
    } catch (err) {
      console.warn("[EventParser] Failed to parse event JSON:", raw);
      return null;
    }
  }
}
