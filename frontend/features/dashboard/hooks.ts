import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from './api';
import { featureFlags } from '@/lib/feature-flags';
import { useDemoStore } from '@/lib/demo/useDemoStore';
import { demoStore } from '@/lib/demo/demoStore';

export function useDashboardOverview() {
  // Always call unconditionally (React hooks rule)
  const demoSnapshot = useDemoStore();

  return useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: dashboardApi.getOverview,
    refetchInterval: featureFlags.DEMO_MODE ? false : 30000,
    ...(featureFlags.DEMO_MODE ? {
      initialData: demoStore.getDashboardOverview() as any,
      initialDataUpdatedAt: demoSnapshot.stats.totalDocuments, // triggers re-render on store updates
    } : {}),
  });
}
