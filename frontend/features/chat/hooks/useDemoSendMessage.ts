/**
 * features/chat/hooks/useDemoSendMessage.ts
 *
 * Demo Mode replacement for useSendMessage.
 * Simulates the full RAG pipeline:
 *   1. Optimistic user message insert
 *   2. "Thinking..." assistant placeholder
 *   3. Animated pipeline status steps in the assistant message
 *   4. Token-by-token streaming of the final answer (word groups)
 *   5. Related questions appended below the answer
 *
 * Contract: drop-in replacement for useSendMessage — same return type.
 */

"use client";

import { useCallback, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { chatKeys } from "@/lib/query-keys";
import { matchIntent, generateConfidence, randomDuration } from "@/lib/demo/intentMatcher";
import { SEARCH_PIPELINE_STEPS } from "@/lib/demo/demoKnowledgeBase";
import { demoStore } from "@/lib/demo/demoStore";

const FALLBACK_ANSWER = `I found several relevant documents in the knowledge base, but couldn't identify a specific best-match for your query.

Try asking about:
- **Hydraulic system inspection** intervals and safety
- **PPE requirements** for production zones
- **Lockout/Tagout** energy isolation procedure
- **Fire emergency** response steps
- **Compressor maintenance** schedules`;

const FALLBACK_QUESTIONS = [
  { text: "What are hydraulic safety protocols?", intentId: "hydraulic" },
  { text: "What PPE is required in production zones?", intentId: "ppe" },
  { text: "Explain the lockout tagout procedure.", intentId: "lockout_tagout" },
];

/** Stream text word-group by word-group, mimicking LLM token streaming. */
async function streamText(
  text: string,
  onChunk: (chunk: string) => void,
  delayMs: [number, number] = [30, 90]
): Promise<void> {
  // Split into word groups of 1-4 words (simulates token bursts)
  const words = text.split(" ");
  let i = 0;
  while (i < words.length) {
    const groupSize = 1 + Math.floor(Math.random() * 3); // 1–3 words
    const chunk = words.slice(i, i + groupSize).join(" ");
    onChunk((i === 0 ? "" : " ") + chunk);
    i += groupSize;
    await new Promise(r => setTimeout(r, randomDuration(delayMs)));
  }
}

export function useDemoSendMessage() {
  const queryClient = useQueryClient();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async ({ conversationId, content }: { conversationId: string; content: string }) => {
      setIsPending(true);

      const queryKey = [...chatKeys.messages(conversationId), 1];
      const userMsgId = `usr_${Date.now()}`;
      const asstMsgId = `ast_${Date.now()}`;
      const now = new Date().toISOString();

      // 1. Optimistic user message
      demoStore.addMessage(conversationId, { id: userMsgId, role: "user", content, createdAt: now });
      queryClient.setQueryData(queryKey, (old: any) => {
        const base = old ?? { items: [], total: 0, page: 1, pageSize: 50, totalPages: 1 };
        return {
          ...base,
          items: [...base.items, { id: userMsgId, conversationId, role: "user", content, status: "COMPLETED", createdAt: now, updatedAt: now }],
          total: base.total + 1,
        };
      });

      // 2. Insert "Thinking..." placeholder
      queryClient.setQueryData(queryKey, (old: any) => ({
        ...old,
        items: [...(old?.items ?? []), {
          id: asstMsgId, conversationId, role: "assistant",
          content: "Thinking...", status: "STREAMING",
          createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
        }],
        total: (old?.total ?? 0) + 1,
      }));

      // 3. Run pipeline steps, displaying them in the assistant message
      const result = matchIntent(content);
      const steps = SEARCH_PIPELINE_STEPS;

      let pipelineText = "";
      for (const step of steps) {
        pipelineText = `*${step.label}*`;
        queryClient.setQueryData(queryKey, (old: any) => ({
          ...old,
          items: old.items.map((m: any) =>
            m.id === asstMsgId ? { ...m, content: pipelineText, status: "STREAMING" } : m
          ),
        }));
        await new Promise(r => setTimeout(r, randomDuration(step.durationRange)));
      }

      // 4. Stream the actual answer word-by-word
      const answer      = result?.entry.answer ?? FALLBACK_ANSWER;
      const confidence  = result
        ? generateConfidence(result.match, result.entry.confidenceRange)
        : null;
      const related     = result?.entry.relatedQuestions ?? FALLBACK_QUESTIONS;

      let streamed = "";
      queryClient.setQueryData(queryKey, (old: any) => ({
        ...old,
        items: old.items.map((m: any) =>
          m.id === asstMsgId ? { ...m, content: "", status: "STREAMING" } : m
        ),
      }));

      await streamText(answer, (chunk) => {
        streamed += chunk;
        queryClient.setQueryData(queryKey, (old: any) => ({
          ...old,
          items: old.items.map((m: any) =>
            m.id === asstMsgId ? { ...m, content: streamed, status: "STREAMING" } : m
          ),
        }));
      });

      // 5. Append confidence + related questions
      const footer = [
        "",
        confidence ? `---\n**Confidence:** ${confidence.toFixed(1)}%` : "",
        related.length > 0
          ? `\n**Suggested Questions:**\n${related.map(q => `- ${q.text}`).join("\n")}`
          : "",
      ].filter(Boolean).join("\n");

      const finalContent = streamed + footer;

      queryClient.setQueryData(queryKey, (old: any) => ({
        ...old,
        items: old.items.map((m: any) =>
          m.id === asstMsgId ? { ...m, content: finalContent, status: "COMPLETED" } : m
        ),
      }));

      // Persist to demo store
      demoStore.addMessage(conversationId, {
        id: asstMsgId, role: "assistant", content: finalContent,
        createdAt: new Date().toISOString(),
      });
      demoStore.recordSearch();

      setIsPending(false);
      return true;
    },
    [queryClient]
  );

  return { mutateAsync, isPending };
}
