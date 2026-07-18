"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const tabs = [
    { name: "Dashboard", href: "/admin/dashboard" },
    { name: "Users", href: "/admin/users" },
    { name: "Documents", href: "/admin/documents" },
    { name: "Jobs", href: "/admin/processing" },
    { name: "System Health", href: "/admin/system" },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto flex flex-col gap-6 w-full animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Administration</h1>
      </div>

      <nav className="flex space-x-4 border-b border-border pb-px">
        {tabs.map((tab) => {
          const isActive = pathname === tab.href;
          return (
            <Link
              key={tab.name}
              href={tab.href}
              className={`pb-2 px-1 border-b-2 transition-colors ${
                isActive
                  ? "border-brand-500 text-brand-600 font-semibold"
                  : "border-transparent text-muted hover:text-foreground hover:border-border"
              }`}
            >
              {tab.name}
            </Link>
          );
        })}
      </nav>

      <main className="w-full">{children}</main>
    </div>
  );
}
