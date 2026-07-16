import React from "react";
import { ChatWorkspace } from "@/features/chat/containers/ChatWorkspace";

export default function ChatIndexPage() {
  // Empty conversationId triggers Welcome Screen inside ChatWorkspace
  return <ChatWorkspace />;
}
