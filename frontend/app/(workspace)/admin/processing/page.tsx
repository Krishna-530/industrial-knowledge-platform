'use client';

import React, { useState } from 'react';
import useSWR from 'swr';
import { api } from '@/lib/api-client';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Pagination } from '@/components/ui/Pagination';
import { Search, Eye, RefreshCw } from 'lucide-react';
import { JobDetailsDialog } from './components/JobDetailsDialog';

interface Job {
  id: string;
  job_type: string;
  status: string;
  attempts: int;
  created_at: string;
  started_at: string | null;
  error_message: string | null;
}

export default function AdminProcessingQueuePage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  
  const limit = 10;
  const offset = (page - 1) * limit;

  const { data, isLoading, mutate } = useSWR<{items: Job[], total: number}>(
    `/admin/jobs?limit=${limit}&offset=${offset}&search=${search}&status=${statusFilter}&job_type=${typeFilter}`, 
    (url) => api.get(url).then(r => r.data)
  );

  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const { data: jobDetails, isLoading: detailsLoading, mutate: mutateDetails } = useSWR(
    selectedJobId ? `/admin/jobs/${selectedJobId}` : null,
    (url) => api.get(url).then(r => r.data)
  );

  const handleRetryJob = async (jobId: string) => {
    try {
      await api.post(`/admin/jobs/${jobId}/retry`);
      mutate();
      if (selectedJobId) {
        mutateDetails();
        setSelectedJobId(null); // Close dialog on retry
      }
    } catch (e: any) {
      alert(`Failed to retry job: ${e.response?.data?.detail || e.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Processing Queue</h2>
        <Button variant="outline" onClick={() => mutate()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Card>
        <CardContent className="p-4 space-y-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search jobs by ID or error..." 
                className="pl-9"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              />
            </div>
            <select 
              className="border border-border rounded-md px-3 py-2 text-sm bg-background"
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            >
              <option value="">All Statuses</option>
              <option value="QUEUED">QUEUED</option>
              <option value="PROCESSING">PROCESSING</option>
              <option value="COMPLETED">COMPLETED</option>
              <option value="FAILED">FAILED</option>
            </select>
            <select 
              className="border border-border rounded-md px-3 py-2 text-sm bg-background"
              value={typeFilter}
              onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
            >
              <option value="">All Types</option>
              <option value="PROCESS_DOCUMENT">PROCESS_DOCUMENT</option>
            </select>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-800 dark:text-gray-400">
                <tr>
                  <th className="px-4 py-3">Job ID</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Started</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr><td colSpan={5} className="text-center py-4">Loading...</td></tr>
                ) : data?.items.length === 0 ? (
                  <tr><td colSpan={5} className="text-center py-4">No jobs found in queue.</td></tr>
                ) : (
                  data?.items.map(job => (
                    <tr key={job.id} className="border-b dark:border-gray-700">
                      <td className="px-4 py-3 font-mono text-xs">{job.id.slice(0, 8)}...</td>
                      <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{job.job_type}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          job.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                          job.status === 'FAILED' ? 'bg-red-100 text-red-800' :
                          job.status === 'PROCESSING' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {job.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">{job.started_at ? new Date(job.started_at).toLocaleString() : '-'}</td>
                      <td className="px-4 py-3 flex gap-2">
                        <Button variant="outline" size="sm" onClick={() => setSelectedJobId(job.id)} title="View Details">
                          <Eye className="w-4 h-4" />
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          <Pagination 
            currentPage={page}
            totalPages={Math.max(1, Math.ceil((data?.total || 0) / limit))}
            onPageChange={setPage}
          />
        </CardContent>
      </Card>

      {selectedJobId && (
        <JobDetailsDialog 
          jobId={selectedJobId} 
          onClose={() => setSelectedJobId(null)} 
          details={jobDetails} 
          isLoading={detailsLoading}
          onRetry={() => handleRetryJob(selectedJobId)}
        />
      )}
    </div>
  );
}
