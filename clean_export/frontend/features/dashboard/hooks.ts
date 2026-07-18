import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from './api';

export function useDashboardOverview() {
  return useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: dashboardApi.getOverview,
    refetchInterval: 30000, // configurable auto-refresh
  });
}
