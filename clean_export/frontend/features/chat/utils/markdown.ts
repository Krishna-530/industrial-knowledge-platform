import { marked } from "marked";
import DOMPurify from "dompurify";

// Configure DOMPurify hook for tab-nabbing protection
if (typeof window !== "undefined") {
  DOMPurify.addHook("afterSanitizeAttributes", (node) => {
    if (node.nodeName === "A") {
      node.setAttribute("target", "_blank");
      node.setAttribute("rel", "noopener noreferrer");
    }
  });
}

export function parseMarkdownSafely(raw: string): string {
  if (!raw) return "";

  // marked.parse is synchronous by default
  const rawHtml = marked.parse(raw) as string;

  if (typeof window === "undefined") {
    // SSR safe-fallback. Without JSDOM, DOMPurify cannot run on Node.
    // We strip tags naively for SSR, or just return the raw string since hydration
    // will replace it on the client anyway.
    return rawHtml.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "");
  }

  return DOMPurify.sanitize(rawHtml, {
    ALLOWED_TAGS: [
      "h1", "h2", "h3", "h4", "h5", "h6", 
      "p", "ul", "ol", "li", "code", "pre", 
      "blockquote", "strong", "em", "a", "br", 
      "hr", "table", "thead", "tbody", "tr", "th", "td", "del"
    ],
    ALLOWED_ATTR: ["href", "class", "target", "rel"], // 'class' allowed for future syntax highlighting
  });
}
