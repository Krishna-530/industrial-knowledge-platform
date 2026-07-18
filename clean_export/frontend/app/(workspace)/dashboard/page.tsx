'use client';

import React from 'react';
import { useDashboardOverview } from '@/features/dashboard/hooks';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { AlertCircle, Database, Server, Link2, Share2, FileText, Activity, Clock } from 'lucide-react';
import { DashboardOverviewResponse } from '@/features/dashboard/types';

function MetricValue({ value, isLoading, unavailable, suffix = '' }: { value?: number | null, isLoading: boolean, unavailable?: boolean, suffix?: string }) {
  if (isLoading) return <Skeleton className="w-16 h-8" />;
  if (unavailable || value === null || value === undefined) return <span className="text-gray-400 text-lg">Unavailable</span>;
  return <span>{value}{suffix}</span>;
}

export default function DashboardPage() {
  const { data, isLoading, isError, refetch } = useDashboardOverview();

  if (isError) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-red-500 flex-col space-y-4">
        <AlertCircle className="w-12 h-12" />
        <p>Failed to load dashboard overview.</p>
        <button onClick={() => refetch()} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto h-[calc(100vh-4rem)] overflow-y-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold dark:text-white">System Overview</h1>
        <button onClick={() => refetch()} className="px-4 py-2 border rounded hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
          Refresh
        </button>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documents Uploaded</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="text-2xl font-bold">
            <MetricValue isLoading={isLoading} value={data?.stats.total_documents} />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Chunks</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="text-2xl font-bold">
            <MetricValue isLoading={isLoading} value={data?.stats.total_chunks} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Entities</CardTitle>
            <Share2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="text-2xl font-bold">
            <MetricValue isLoading={isLoading} value={data?.stats.total_entities} />
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Knowledge Graph */}
        <Card className="col-span-1">
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
              <span className="text-sm text-gray-500">Edges</span>
              <span className="font-semibold"><MetricValue isLoading={isLoading} value={data?.graph.total_edges} /></span>
            </div>
            <div className="flex justify-between items-center border-b pb-2">
              <span className="text-sm text-gray-500">Sync Lag</span>
              <span className="font-semibold text-gray-400">
                <MetricValue isLoading={isLoading} unavailable={true} />
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Graph Health</span>
              <span className="font-semibold text-gray-400">Unavailable</span>
            </div>
          </CardContent>
        </Card>

        {/* Worker Status */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="w-5 h-5 text-green-500" />
              Worker Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center border-b pb-2">
              <span className="text-sm text-gray-500">Queued</span>
              <span className="font-semibold"><MetricValue isLoading={isLoading} value={data?.workers.queued} /></span>
            </div>
            <div className="flex justify-between items-center border-b pb-2">
              <span className="text-sm text-gray-500">Processing</span>
              <span className="font-semibold text-blue-600"><MetricValue isLoading={isLoading} value={data?.workers.processing} /></span>
            </div>
            <div className="flex justify-between items-center border-b pb-2">
              <span className="text-sm text-gray-500">Failed</span>
              <span className="font-semibold text-red-500"><MetricValue isLoading={isLoading} value={data?.workers.failed} /></span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Total Processed</span>
              <span className="font-semibold"><MetricValue isLoading={isLoading} value={data?.workers.total} /></span>
            </div>
          </CardContent>
        </Card>

        {/* Retrieval Statistics */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-purple-500" />
              Retrieval Statistics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center border-b pb-2">
              <span className="text-sm text-gray-500">Total Searches</span>
              <span className="font-semibold">
                <MetricValue isLoading={isLoading} value={data?.retrieval.total_searches} unavailable={data?.retrieval.status === 'unavailable'} />
              </span>
            </div>
            <div className="flex justify-between items-center border-b pb-2">
              <span className="text-sm text-gray-500">Avg Retrieval Time</span>
              <span className="font-semibold">
                <MetricValue isLoading={isLoading} value={data?.retrieval.average_latency} suffix="ms" unavailable={data?.retrieval.status === 'unavailable'} />
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Cache Hit Ratio</span>
              <span className="font-semibold text-gray-400">Unavailable</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tables Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent Documents */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Documents</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="w-full h-10" />
                <Skeleton className="w-full h-10" />
                <Skeleton className="w-full h-10" />
              </div>
            ) : data?.recent_documents.length === 0 ? (
              <div className="text-center py-6 text-gray-500">No documents uploaded yet.</div>
            ) : (
              <div className="space-y-3">
                {data?.recent_documents.map(doc => (
                  <div key={doc.id} className="flex justify-between items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded">
                    <div>
                      <p className="font-medium text-sm truncate max-w-[200px]">{doc.title}</p>
                      <p className="text-xs text-gray-500">{new Date(doc.uploaded_at).toLocaleString()}</p>
                    </div>
                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">{doc.status}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Jobs */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Background Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="w-full h-10" />
                <Skeleton className="w-full h-10" />
                <Skeleton className="w-full h-10" />
              </div>
            ) : data?.processing_queue.length === 0 ? (
              <div className="text-center py-6 text-gray-500">No jobs processed yet.</div>
            ) : (
              <div className="space-y-3">
                {data?.processing_queue.map(job => (
                  <div key={job.job_id} className="flex justify-between items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded">
                    <div>
                      <p className="font-medium text-sm text-gray-800 dark:text-gray-200">{job.job_type}</p>
                      <p className="text-xs text-gray-500 font-mono truncate max-w-[150px]">{job.job_id}</p>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-1 text-xs rounded ${job.status === 'FAILED' ? 'bg-red-100 text-red-800' : job.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`}>
                        {job.status}
                      </span>
                      {job.started_at && <p className="text-xs text-gray-500 mt-1">{new Date(job.started_at).toLocaleTimeString()}</p>}
                    </div>
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
