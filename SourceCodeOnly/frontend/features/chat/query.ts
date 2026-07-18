import { queryKeys } from "@/lib/query-keys";

export const chatQueryKeys = {
  list:   queryKeys.conversations,
  detail: (id: string) => queryKeys.conversation(id),
};
