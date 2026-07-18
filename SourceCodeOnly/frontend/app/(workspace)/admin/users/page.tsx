'use client';

import React, { useState } from 'react';
import useSWR from 'swr';
import { api } from '@/lib/api-client';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Pagination } from '@/components/ui/Pagination';
import { Search, UserCheck, UserX, Trash2 } from 'lucide-react';

interface User {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  role: { name: string };
  created_at: string;
}

export default function AdminUsersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const limit = 10;
  const offset = (page - 1) * limit;

  const { data, isLoading, mutate } = useSWR<{items: User[], total: number}>(
    `/admin/users?limit=${limit}&offset=${offset}&search=${search}`, 
    (url) => api.get(url).then(r => r.data)
  );

  const toggleUserStatus = async (user: User) => {
    try {
      if (user.is_active) {
        await api.patch(`/users/${user.id}/deactivate`);
      } else {
        await api.patch(`/users/${user.id}/activate`);
      }
      mutate();
    } catch (e) {
      console.error(e);
    }
  };

  const deleteUser = async (id: string) => {
    if (confirm("Are you sure you want to delete this user?")) {
      try {
        await api.delete(`/users/${id}`);
        mutate();
      } catch (e) {
        console.error(e);
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">User Management</h2>
        {/* We can add a create user dialog trigger here if needed */}
      </div>

      <Card>
        <CardContent className="p-4 space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search users by name or email..." 
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
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr><td colSpan={5} className="text-center py-4">Loading...</td></tr>
                ) : data?.items.length === 0 ? (
                  <tr><td colSpan={5} className="text-center py-4">No users found.</td></tr>
                ) : (
                  data?.items.map(user => (
                    <tr key={user.id} className="border-b dark:border-gray-700">
                      <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{user.name}</td>
                      <td className="px-4 py-3">{user.email}</td>
                      <td className="px-4 py-3">{user.role?.name || 'Unknown'}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {user.is_active ? 'Active' : 'Disabled'}
                        </span>
                      </td>
                      <td className="px-4 py-3 flex gap-2">
                        <Button variant="outline" size="sm" onClick={() => toggleUserStatus(user)}>
                          {user.is_active ? <UserX className="w-4 h-4 text-red-500" /> : <UserCheck className="w-4 h-4 text-green-500" />}
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => deleteUser(user.id)}>
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
