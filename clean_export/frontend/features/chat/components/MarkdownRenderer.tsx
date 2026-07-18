"use client";

import React, { useMemo, useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { parseMarkdownSafely } from "../utils/markdown";
import { CitationBadge } from "./CitationBadge";

interface MarkdownRendererProps {
  content: string;
  isStreaming?: boolean;
}

export const MarkdownRenderer = React.memo(({ content, isStreaming }: MarkdownRendererProps) => {
  // Throttle content updates during streaming to avoid thread-blocking
  // caused by running marked + DOMPurify 20+ times per second.
  const [throttledContent, setThrottledContent] = useState(content);

  useEffect(() => {
    if (!isStreaming) {
      setThrottledContent(content);
      return;
    }

    const timeout = setTimeout(() => {
      setThrottledContent(content);
    }, 100);

    return () => clearTimeout(timeout);
  }, [content, isStreaming]);

  const html = useMemo(() => {
    let rawHtml = parseMarkdownSafely(throttledContent);
    // Replace [id] or [cite:id] with a placeholder for the portal
    // Assuming citation format: [cite:uuid] or just UUIDs in brackets
    // Let's support [uuid]
    const uuidRegex = /\[([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\]/gi;
    rawHtml = rawHtml.replace(uuidRegex, '<span class="citation-placeholder" data-rel-id="$1"></span>');
    return rawHtml;
  }, [throttledContent]);

  const containerRef = useRef<HTMLDivElement>(null);
  const [portals, setPortals] = useState<React.ReactPortal[]>([]);

  useEffect(() => {
    if (!containerRef.current) return;
    const placeholders = containerRef.current.querySelectorAll('.citation-placeholder');
    const newPortals: React.ReactPortal[] = [];
    
    placeholders.forEach((el, index) => {
      const relId = el.getAttribute('data-rel-id');
      if (relId) {
        newPortals.push(
          createPortal(
            <CitationBadge relationshipId={relId} index={index + 1} />,
            el
          )
        );
      }
    });
    
    setPortals(newPortals);
  }, [html]);

  return (
    <div className="relative">
      <div 
        ref={containerRef}
        className="markdown-body max-w-none break-words space-y-4"
        dangerouslySetInnerHTML={{ __html: html }}
      />
      {portals}
    </div>
  );
});

MarkdownRenderer.displayName = "MarkdownRenderer";
