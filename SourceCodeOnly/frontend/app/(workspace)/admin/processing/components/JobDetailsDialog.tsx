import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { X, RefreshCw } from 'lucide-react';

interface JobDetailsDialogProps {
  jobId: string;
  onClose: () => void;
  onRetry: () => void;
  details: any;
  isLoading: boolean;
}

export function JobDetailsDialog({ jobId, onClose, onRetry, details, isLoading }: JobDetailsDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-background rounded-xl shadow-xl w-full max-w-3xl flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-xl font-bold">Job Details Inspection</h2>
          <Button variant="outline" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6 overflow-y-auto space-y-6">
          {isLoading ? (
            <div className="text-center text-muted-foreground py-8">Loading details...</div>
          ) : !details ? (
            <div className="text-center text-red-500 py-8">Failed to load details.</div>
          ) : (
            <>
              {/* Job Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Job ID</p>
                  <p className="font-mono text-sm">{details.job?.id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Type</p>
                  <p className="font-medium">{details.job?.job_type}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    details.job?.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                    details.job?.status === 'FAILED' ? 'bg-red-100 text-red-800' :
                    details.job?.status === 'PROCESSING' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {details.job?.status}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Retry Count</p>
                  <p className="font-medium">{details.job?.attempts} / {details.job?.max_attempts}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Started</p>
                  <p className="font-medium">{details.job?.started_at ? new Date(details.job.started_at).toLocaleString() : 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Finished</p>
                  <p className="font-medium">{details.job?.completed_at || details.job?.failed_at ? new Date(details.job.completed_at || details.job.failed_at).toLocaleString() : 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Duration</p>
                  <p className="font-medium">
                    {details.job?.started_at && (details.job?.completed_at || details.job?.failed_at)
                      ? `${Math.round((new Date(details.job.completed_at || details.job.failed_at).getTime() - new Date(details.job.started_at).getTime()) / 1000)}s`
                      : 'N/A'
                    }
                  </p>
                </div>
              </div>

              {/* Document Info if available */}
              {details.document && (
                <div className="border-t border-border pt-6">
                  <h3 className="text-lg font-semibold mb-4">Document</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Title</p>
                      <p className="font-medium">{details.document.title}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Pipeline Timeline */}
              <div className="border-t border-border pt-6">
                <h3 className="text-lg font-semibold mb-4">Pipeline Timeline & Stages</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 rounded-lg border border-border">
                    <span className="font-medium text-sm">1. Job Queue</span>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded font-semibold">{details.job?.status}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 rounded-lg border border-border">
                    <span className="font-medium text-sm">2. Content Processing (OCR/Text)</span>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded font-semibold">{details.document_content?.processing_status || 'PENDING'}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 rounded-lg border border-border">
                    <span className="font-medium text-sm">3. Entity Extraction</span>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded font-semibold">{details.document?.extraction_status || 'PENDING'}</span>
                  </div>
                </div>
              </div>

              {/* Error */}
              {details.job?.error_message && (
                <div className="border-t border-border pt-6">
                  <h3 className="text-lg font-semibold text-red-500 mb-2">Error Logs</h3>
                  <pre className="bg-red-50 text-red-900 p-4 rounded text-xs overflow-x-auto whitespace-pre-wrap">
                    {details.job.error_message}
                  </pre>
                </div>
              )}
            </>
          )}
        </div>

        <div className="flex items-center justify-end p-6 border-t border-border gap-3">
          <Button variant="outline" onClick={onClose}>Close</Button>
          {details?.job && (details.job.status === 'FAILED' || details.job.is_dead_letter) && (
            <Button className="bg-blue-600 hover:bg-blue-700 text-white" onClick={onRetry}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry Job
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
