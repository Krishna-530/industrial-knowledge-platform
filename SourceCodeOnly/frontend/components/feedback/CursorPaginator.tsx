"use client";

import { ChevronLeftIcon, ChevronRightIcon } from "@/lib/icons";
import type { CursorPage } from "@/types/api";

interface CursorPaginatorProps<T> {
  page: CursorPage<T>;
  onNextPage: (cursor: string) => void;
  onPrevPage: () => void;
  hasPrev: boolean;
}

/**
 * CursorPaginator — UI only component for cursor-based pagination.
 * Does NOT own data fetching or state. Delegates via onNextPage / onPrevPage.
 */
export default function CursorPaginator<T>({
  page,
  onNextPage,
  onPrevPage,
  hasPrev,
}: CursorPaginatorProps<T>) {
  return (
    <div className="flex items-center justify-between border-t border-border bg-surface px-4 py-3 sm:px-6">
      <div className="flex flex-1 justify-between sm:hidden">
        <button
          onClick={onPrevPage}
          disabled={!hasPrev}
          className="relative inline-flex items-center rounded-md border border-border bg-surface px-4 py-2 text-sm font-medium text-foreground hover:bg-background disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          onClick={() => page.next_cursor && onNextPage(page.next_cursor)}
          disabled={!page.has_more || !page.next_cursor}
          className="relative ml-3 inline-flex items-center rounded-md border border-border bg-surface px-4 py-2 text-sm font-medium text-foreground hover:bg-background disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
      <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-muted">
            Showing <span className="font-medium">{page.items.length}</span> results
          </p>
        </div>
        <div>
          <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
            <button
              onClick={onPrevPage}
              disabled={!hasPrev}
              className="relative inline-flex items-center rounded-l-md px-2 py-2 text-muted ring-1 ring-inset ring-border hover:bg-background focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="sr-only">Previous</span>
              <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
            </button>
            <button
              onClick={() => page.next_cursor && onNextPage(page.next_cursor)}
              disabled={!page.has_more || !page.next_cursor}
              className="relative inline-flex items-center rounded-r-md px-2 py-2 text-muted ring-1 ring-inset ring-border hover:bg-background focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="sr-only">Next</span>
              <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
            </button>
          </nav>
        </div>
      </div>
    </div>
  );
}
