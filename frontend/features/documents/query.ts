import { queryKeys } from "@/lib/query-keys";

export const documentQueryKeys = {
  list:   queryKeys.documents,
  detail: (id: string) => queryKeys.document(id),
};
