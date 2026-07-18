import { apiClient } from '@/lib/api-client';
import { DashboardOverviewResponse } from './types';

export const dashboardApi = {
  getOverview: async (): Promise<DashboardOverviewResponse> => {
    return apiClient<DashboardOverviewResponse>({
      endpoint: '/dashboard/overview',
      method: 'GET',
    });
  }
};
