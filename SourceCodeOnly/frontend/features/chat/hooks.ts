import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { chatKeys } from "@/lib/query-keys";
import { 
  getConversations, 
  getConversationDetails, 
  getMessages, 
  createConversation, 
  deleteConversation,
  sendMessage 
} from "./api";
import type { Message } from "./types";

export function useConversations(page: number = 1) {
  return useQuery({
    queryKey: [...chatKeys.lists(), page],
    queryFn: () => getConversations(page, 20),
    staleTime: 60 * 1000, // 1 minute
  });
}

export function useConversation(id: string) {
  return useQuery({
    queryKey: chatKeys.detail(id),
    queryFn: () => getConversationDetails(id),
    enabled: !!id,
    staleTime: 60 * 1000,
  });
}

export function useMessages(conversationId: string, page: number = 1) {
  return useQuery({
    queryKey: [...chatKeys.messages(conversationId), page],
    queryFn: () => getMessages(conversationId, page, 50),
    enabled: !!conversationId,
    staleTime: Infinity,
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => createConversation(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: chatKeys.lists() });
    },
  });
}

export function useDeleteConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteConversation(id),
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: chatKeys.lists() });
      queryClient.removeQueries({ queryKey: chatKeys.detail(deletedId) });
      queryClient.removeQueries({ queryKey: chatKeys.messages(deletedId) });
    },
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ conversationId, content }: { conversationId: string; content: string }) => {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
      const token = document.cookie.replace(/(?:(?:^|.*;\s*)auth_token\s*\=\s*([^;]*).*$)|^.*$/, "$1");
      
      const response = await fetch(`${baseUrl}/retrieval/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          search_query: { text: content },
          latest_only: true,
          include_metadata: true,
          include_content: true
        })
      });

      if (!response.ok) throw new Error("Stream failed");
      
      const reader = response.body?.getReader();
      if (!reader) throw new Error("No reader");

      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      
      const queryKey = [...chatKeys.messages(conversationId), 1];
      const assistantMsgId = `ast_${Date.now()}`;
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() || "";

        for (const chunk of chunks) {
          if (!chunk.trim()) continue;
          
          const eventMatch = chunk.match(/event:\s*(.+)/);
          const dataMatch = chunk.match(/data:\s*(.+)/);
          
          if (eventMatch && dataMatch) {
            const eventName = eventMatch[1].trim();
            const payload = JSON.parse(dataMatch[1].trim());

            if (eventName === "message") {
              const deltaContent = payload.results ? JSON.stringify(payload.results) : (payload.source || "Processing...");
              
              queryClient.setQueryData(queryKey, (old: any) => {
                if (!old) return old;
                
                // See if assistant message exists
                const exists = old.items.some((m: any) => m.id === assistantMsgId);
                if (!exists) {
                  return {
                    ...old,
                    items: [...old.items, {
                      id: assistantMsgId,
                      conversationId,
                      role: "assistant",
                      content: deltaContent + "\n",
                      status: "STREAMING",
                      createdAt: new Date().toISOString(),
                      updatedAt: new Date().toISOString()
                    }],
                    total: old.total + 1
                  };
                } else {
                  return {
                    ...old,
                    items: old.items.map((msg: any) => 
                      msg.id === assistantMsgId 
                        ? { ...msg, content: msg.content + deltaContent + "\n" }
                        : msg
                    )
                  };
                }
              });
            } else if (eventName === "complete" || eventName === "disconnect") {
              queryClient.setQueryData(queryKey, (old: any) => {
                if (!old) return old;
                return {
                  ...old,
                  items: old.items.map((msg: any) => 
                    msg.id === assistantMsgId 
                      ? { ...msg, status: "COMPLETED" }
                      : msg
                  )
                };
              });
            } else if (eventName === "error") {
              queryClient.setQueryData(queryKey, (old: any) => {
                if (!old) return old;
                return {
                  ...old,
                  items: old.items.map((msg: any) => 
                    msg.id === assistantMsgId 
                      ? { ...msg, status: "FAILED", content: msg.content + "\nError: " + payload.detail }
                      : msg
                  )
                };
              });
            }
          }
        }
      }
      return true;
    },
    
    onMutate: async ({ conversationId, content }) => {
      const queryKey = [...chatKeys.messages(conversationId), 1];
      await queryClient.cancelQueries({ queryKey });
      const previousMessages = queryClient.getQueryData(queryKey);
      
      const userMsgId = `usr_${Date.now()}`;
      const optimisticMessage: Message = {
        id: userMsgId,
        conversationId,
        role: "user",
        content,
        status: "COMPLETED",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      queryClient.setQueryData(queryKey, (old: any) => {
        if (!old) return { items: [optimisticMessage], total: 1, page: 1, pageSize: 50, totalPages: 1 };
        return {
          ...old,
          items: [...old.items, optimisticMessage],
          total: old.total + 1,
        };
      });
      
      return { previousMessages, queryKey };
    },
    
    onError: (err, variables, context) => {
      if (context?.previousMessages) {
        queryClient.setQueryData(context.queryKey, context.previousMessages);
      }
    },
    
    onSettled: (data, error, variables, context) => {
      // Don't refetch automatically to prevent wiping streaming updates
    },
  });
}
