import React from "react";
import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import { Pagination, type PaginationProps } from "./Pagination";

export interface Column<T> {
  key: string;
  header: string;
  sortable?: boolean;
  render?: (row: T) => React.ReactNode;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: Extract<keyof T, string> | ((row: T) => string);
  
  // States
  isLoading?: boolean;
  emptyState?: React.ReactNode;
  errorState?: React.ReactNode;
  
  // Slots
  toolbar?: React.ReactNode;
  actions?: (row: T) => React.ReactNode;
  
  // Pagination
  pagination?: Omit<PaginationProps, "isLoading">;
  
  // Sorting
  currentSort?: { key: string; direction: "asc" | "desc" };
  onSortChange?: (key: string, direction: "asc" | "desc") => void;
}

export function DataTable<T>({
  columns,
  rows,
  rowKey,
  isLoading,
  emptyState,
  errorState,
  toolbar,
  actions,
  pagination,
  currentSort,
  onSortChange,
}: DataTableProps<T>) {

  const getRowKey = (row: T): string => {
    if (typeof rowKey === "function") {
      return rowKey(row);
    }
    return String(row[rowKey]);
  };

  const handleSort = (key: string) => {
    if (!onSortChange) return;
    
    if (currentSort?.key === key) {
      onSortChange(key, currentSort.direction === "asc" ? "desc" : "asc");
    } else {
      onSortChange(key, "asc");
    }
  };

  const renderSortIcon = (key: string) => {
    if (currentSort?.key !== key) {
      return <ArrowUpDown className="w-4 h-4 ml-1 text-gray-400 group-hover:text-gray-500" />;
    }
    return currentSort.direction === "asc" ? (
      <ArrowUp className="w-4 h-4 ml-1 text-gray-900 dark:text-gray-100" />
    ) : (
      <ArrowDown className="w-4 h-4 ml-1 text-gray-900 dark:text-gray-100" />
    );
  };

  return (
    <div className="flex flex-col w-full bg-white dark:bg-gray-900 rounded-lg shadow ring-1 ring-black ring-opacity-5">
      {toolbar && (
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          {toolbar}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-800" aria-busy={isLoading}>
          <thead className="bg-gray-50 dark:bg-gray-800/50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  scope="col"
                  className={`px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider ${
                    col.sortable ? "cursor-pointer group hover:bg-gray-100 dark:hover:bg-gray-800" : ""
                  }`}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center">
                    {col.header}
                    {col.sortable && renderSortIcon(col.key)}
                  </div>
                </th>
              ))}
              {actions && (
                <th scope="col" className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
            {errorState ? (
              <tr>
                <td colSpan={columns.length + (actions ? 1 : 0)} className="px-6 py-12">
                  {errorState}
                </td>
              </tr>
            ) : rows.length === 0 && !isLoading ? (
              <tr>
                <td colSpan={columns.length + (actions ? 1 : 0)} className="px-6 py-12">
                  {emptyState}
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr key={getRowKey(row)} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                  {columns.map((col) => (
                    <td key={col.key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {col.render ? col.render(row) : String(row[col.key as keyof T] ?? "")}
                    </td>
                  ))}
                  {actions && (
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {actions(row)}
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {pagination && (
        <Pagination
          {...pagination}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}
