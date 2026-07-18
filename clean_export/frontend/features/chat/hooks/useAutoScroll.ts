import { useEffect, useRef, useCallback } from "react";

export function useAutoScroll<T extends HTMLElement>(dependencies: any[]) {
  const containerRef = useRef<T>(null);
  const isAtBottomRef = useRef(true);

  const handleScroll = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;

    const threshold = 100; // pixels from the bottom to consider "at bottom"
    const distanceToBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
    
    isAtBottomRef.current = distanceToBottom <= threshold;
  }, []);

  const scrollToBottom = useCallback((behavior: ScrollBehavior = "smooth") => {
    const container = containerRef.current;
    if (!container) return;
    
    container.scrollTo({
      top: container.scrollHeight,
      behavior,
    });
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener("scroll", handleScroll);
    }
    return () => {
      if (container) {
        container.removeEventListener("scroll", handleScroll);
      }
    };
  }, [handleScroll]);

  // Auto-scroll when dependencies change, but only if we were already at the bottom
  useEffect(() => {
    if (isAtBottomRef.current) {
      scrollToBottom();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return { containerRef, scrollToBottom };
}
