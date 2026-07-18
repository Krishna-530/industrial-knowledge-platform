'use client';

import React from 'react';
import useSWR from 'swr';
import { api } from '@/lib/api-client';
import { AdminDashboardOverviewResponse } from '@/features/dashboard/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { Users, FileText, Database, Share2, Server, Activity, Clock } from 'lucide-react';

function MetricValue({ value, isLoading, unavailable, suffix = '' }: { value?: number | null, isLoading: boolean, unavailable?: boolean, suffix?: string }) {
  if (isLoading) return <Skeleton className="w-16 h-8" />;
  if (unavailable || value === null || value === undefined) return <span className="text-gray-400 text-lg">Unavailable</span>;
  return <span>{value}{suffix}</span>;
}

export default function AdminDashboardPage() {
  const { data, isLoading, error, mutate } = useSWR<AdminDashboardOverviewResponse>('/admin/dashboard', (url) => api.get(url).then(r => r.data));

  if (error) {
    return (
      <div className="flex h-64 items-center justify-center text-red-500 flex-col space-y-4">
        <p>Failed to load admin dashboard overview.</p>
        <button onClick={() => mutate()} className="px-4 py-2 border rounded hover:bg-gray-50 transition-colors">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Admin Overview</h2>
        <button onClick={() => mutate()} className="px-4 py-2 border rounded hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="text-2xl font-bold text-brand-600">
            <MetricValue isLoading={isLoading} value={data?.stats.total_users} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="text-2xl font-bold">
            <MetricValue isLoading={isLoading} value={data?.stats.total_documents} />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processing Jobs</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="text-2xl font-bold">
            <MetricValue isLoading={isLoading} value={data?.workers.processing} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed Jobs</CardTitle>
            <Server className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent className="text-2xl font-bold text-red-500">
            <MetricValue isLoading={isLoading} value={data?.workers.failed} />
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Share2 className="w-5 h-5 text-blue-500" />
              Knowledge Graph
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center border-b pb-2">
              <span className="text-sm text-gray-500">Nodes</span>
              <span className="font-semibold"><MetricValue isLoading={isLoading} value={data?.graph.total_nodes} /></span>
            </div>
            <div className="flex justify-between items-center border-b pb-2">
              <span className="text-sm text-gray-500">Relationships</span>
              <span className="font-semibold"><MetricValue isLoading={isLoading} value={data?.graph.total_edges} /></span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="w-full h-8" />
                <Skeleton className="w-full h-8" />
              </div>
            ) : data?.recent_documents.length === 0 ? (
              <div className="text-center py-6 text-gray-500">No recent activity.</div>
            ) : (
              <div className="space-y-3">
                {data?.recent_documents.slice(0, 5).map(doc => (
                  <div key={doc.id} className="flex justify-between items-center border-b pb-2">
                    <p className="font-medium text-sm truncate max-w-[200px]">{doc.title}</p>
                    <span className="px-2 py-1 text-xs bg-gray-100 rounded">{doc.status}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
