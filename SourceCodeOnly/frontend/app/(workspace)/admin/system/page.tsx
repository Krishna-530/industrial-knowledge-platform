'use client';

import React from 'react';
import useSWR from 'swr';
import { api } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { RefreshCw, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

interface HealthCheckResult {
  service: string;
  status: string;
  latency: number;
  message: string;
}

interface SystemHealthResponse {
  services: HealthCheckResult[];
  last_checked: string;
}

export default function SystemHealthPage() {
  const { data, isLoading, mutate } = useSWR<SystemHealthResponse>(
    '/admin/health',
    (url) => api.get(url).then(r => r.data)
  );

  const healthyCount = data?.services.filter(s => s.status === 'Healthy').length || 0;
  const warningCount = data?.services.filter(s => s.status === 'Warning').length || 0;
  const offlineCount = data?.services.filter(s => s.status === 'Offline').length || 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">System Health</h2>
        <Button variant="outline" onClick={() => mutate()} disabled={isLoading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Infrastructure Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="flex flex-col items-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <CheckCircle2 className="w-8 h-8 text-green-500 mb-2" />
              <span className="text-2xl font-bold text-green-700 dark:text-green-400">{healthyCount}</span>
              <span className="text-sm font-medium text-green-600 dark:text-green-500">Healthy</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <AlertTriangle className="w-8 h-8 text-yellow-500 mb-2" />
              <span className="text-2xl font-bold text-yellow-700 dark:text-yellow-400">{warningCount}</span>
              <span className="text-sm font-medium text-yellow-600 dark:text-yellow-500">Warning</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <XCircle className="w-8 h-8 text-red-500 mb-2" />
              <span className="text-2xl font-bold text-red-700 dark:text-red-400">{offlineCount}</span>
              <span className="text-sm font-medium text-red-600 dark:text-red-500">Offline</span>
            </div>
            <div className="flex flex-col items-center justify-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-border">
              <span className="text-sm text-muted-foreground mb-1">Last Updated</span>
              <span className="text-lg font-mono font-medium">
                {data?.last_checked ? new Date(data.last_checked).toLocaleTimeString() : '--:--:--'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Detailed Service Checks</CardTitle>
        </CardHeader>
        <CardContent className="!p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-800 dark:text-gray-400">
                <tr>
                  <th className="px-6 py-3">Service</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Response Time</th>
                  <th className="px-6 py-3">Message</th>
                </tr>
              </thead>
              <tbody>
                {isLoading && !data ? (
                  <tr><td colSpan={4} className="text-center py-8">Checking infrastructure...</td></tr>
                ) : data?.services.map(service => (
                  <tr key={service.service} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">{service.service}</td>
                    <td className="px-6 py-4">
                      <span className={`flex items-center gap-2 font-semibold ${
                        service.status === 'Healthy' ? 'text-green-600' :
                        service.status === 'Warning' ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {service.status === 'Healthy' ? <CheckCircle2 className="w-4 h-4" /> :
                         service.status === 'Warning' ? <AlertTriangle className="w-4 h-4" /> :
                         <XCircle className="w-4 h-4" />}
                        {service.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-muted-foreground">{service.latency} ms</td>
                    <td className="px-6 py-4 text-muted-foreground">{service.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
