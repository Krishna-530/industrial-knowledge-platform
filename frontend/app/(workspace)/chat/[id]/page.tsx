import React from "react";
import { ChatWorkspace } from "@/features/chat/containers/ChatWorkspace";

export default function ChatDetailPage({ params }: { params: { id: string } }) {
  return <ChatWorkspace conversationId={params.id} />;
}
