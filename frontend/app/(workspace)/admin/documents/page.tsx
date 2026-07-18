'use client';

import React, { useState } from 'react';
import useSWR from 'swr';
import { api } from '@/lib/api-client';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Pagination } from '@/components/ui/Pagination';
import { Search, Trash2, RefreshCw, FileText } from 'lucide-react';

interface Document {
  id: string;
  title: string;
  status: string;
  created_at: string;
  owner: { name: string; email: string };
}

export default function AdminDocumentsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const limit = 10;
  const offset = (page - 1) * limit;

  const { data, isLoading, mutate } = useSWR<{items: Document[], total: number}>(
    `/admin/documents?limit=${limit}&offset=${offset}&title_search=${search}`, 
    (url) => api.get(url).then(r => r.data)
  );

  const deleteDocument = async (id: string) => {
    if (confirm("Are you sure you want to delete this document? This cannot be undone.")) {
      try {
        await api.delete(`/documents/${id}`);
        mutate();
      } catch (e) {
        console.error(e);
      }
    }
  };

  const reprocessDocument = async (id: string) => {
    if (confirm("Queue this document for reprocessing?")) {
      try {
        await api.post(`/admin/documents/${id}/reprocess`);
        mutate();
      } catch (e) {
        console.error(e);
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Document Management</h2>
      </div>

      <Card>
        <CardContent className="p-4 space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search documents by title..." 
                className="pl-9"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-800 dark:text-gray-400">
                <tr>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Owner</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr><td colSpan={5} className="text-center py-4">Loading...</td></tr>
                ) : data?.items.length === 0 ? (
                  <tr><td colSpan={5} className="text-center py-4">No documents found.</td></tr>
                ) : (
                  data?.items.map(doc => (
                    <tr key={doc.id} className="border-b dark:border-gray-700">
                      <td className="px-4 py-3 font-medium text-gray-900 dark:text-white flex items-center gap-2">
                        <FileText className="w-4 h-4 text-muted-foreground" />
                        {doc.title}
                      </td>
                      <td className="px-4 py-3">{doc.owner?.name || 'Unknown'}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs ${doc.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : doc.status === 'FAILED' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'}`}>
                          {doc.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">{new Date(doc.created_at).toLocaleDateString()}</td>
                      <td className="px-4 py-3 flex gap-2">
                        <Button variant="outline" size="sm" onClick={() => reprocessDocument(doc.id)} title="Reprocess">
                          <RefreshCw className="w-4 h-4 text-blue-500" />
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => deleteDocument(doc.id)} title="Delete">
                          <Trash2 className="w-4 h-4 text-red-500" />
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
            totalPages={Math.ceil((data?.total || 0) / limit)}
            onPageChange={setPage}
          />
        </CardContent>
      </Card>
    </div>
  );
}
