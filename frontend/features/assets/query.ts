import { queryKeys } from "@/lib/query-keys";

export const assetQueryKeys = {
  list:     queryKeys.assets,
  detail:   (id: string) => queryKeys.asset(id),
  facts:    (id: string) => queryKeys.assetFacts(id),
  findings: (id: string) => queryKeys.assetFindings(id),
};
