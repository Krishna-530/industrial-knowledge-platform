"use client";

import { useState, useEffect } from "react";
import { navigationItems } from "@/lib/navigation";
import { checkPermission } from "@/lib/auth/authorization";
import { useCurrentUser } from "@/features/auth/hooks";
import { featureFlags } from "@/lib/feature-flags";
import Link from "next/link";
import { usePathname } from "next/navigation";
import * as Icons from "@/lib/icons";
import type { NavItem } from "@/types/app";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

function SidebarItem({ item, isActive, isCollapsed, user, onClick }: { item: NavItem, isActive: boolean, isCollapsed: boolean, user: any, onClick?: () => void }) {
  // Guard by feature flag
  if (item.featureFlag && !featureFlags[item.featureFlag as keyof typeof featureFlags]) {
    return null;
  }

  // Guard by permission
  const hasAccess = item.permission ? checkPermission(user, item.permission) : true;
  if (!hasAccess) return null;

  const Icon = (Icons as any)[item.iconName] || Icons.InfoIcon;

  return (
    <li>
      <Link
        href={item.href}
        onClick={onClick}
        className={cn(
          "flex items-center rounded-lg transition-all duration-150 text-sm font-medium",
          isCollapsed ? "justify-center p-3" : "gap-3 px-3 py-2",
          isActive 
            ? "bg-brand-50 text-brand-600 dark:bg-[#1E3A8A]/30 dark:text-brand-500" 
            : "text-muted hover:text-foreground hover:bg-gray-100 dark:hover:bg-white/5"
        )}
        title={isCollapsed ? item.title : undefined}
      >
        <Icon className={cn("flex-shrink-0", isCollapsed ? "h-6 w-6" : "h-5 w-5")} />
        {!isCollapsed && <span>{item.title}</span>}
      </Link>
    </li>
  );
}

interface SidebarProps {
  isMobileOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({ isMobileOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { data: user } = useCurrentUser();

  // Restore desktop collapse state
  useEffect(() => {
    const saved = localStorage.getItem("sidebar-collapsed");
    if (saved === "1") {
      setIsCollapsed(true);
    }
  }, []);

  const toggleCollapse = () => {
    const next = !isCollapsed;
    setIsCollapsed(next);
    localStorage.setItem("sidebar-collapsed", next ? "1" : "0");
  };

  return (
    <>
      {/* Mobile Drawer Overlay */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 md:hidden animate-fade-in"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside 
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex flex-col bg-surface border-r border-border transition-all duration-300 ease-in-out md:static md:translate-x-0 h-full dark:bg-[#111827]",
          isCollapsed ? "w-20" : "w-64",
          isMobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo Area */}
        <div className="p-4 border-b border-border h-16 flex items-center justify-between flex-shrink-0">
          <div className={cn("font-bold text-foreground overflow-hidden whitespace-nowrap transition-all", isCollapsed ? "w-0 opacity-0" : "w-auto opacity-100")}>
            Platform
          </div>
          
          <button
            onClick={toggleCollapse}
            className="hidden md:flex p-1.5 text-muted hover:text-foreground rounded-md hover:bg-background transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 flex-shrink-0"
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? <Icons.MenuIcon className="h-5 w-5" /> : <Icons.ChevronLeftIcon className="h-5 w-5" />}
          </button>

          <button
            onClick={onClose}
            className="md:hidden p-1.5 text-muted hover:text-foreground rounded-md focus:outline-none"
            aria-label="Close menu"
          >
            <Icons.XIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation Area */}
        <nav className="flex-1 overflow-y-auto py-4 overflow-x-hidden">
          <ul className="space-y-1 px-3">
            {navigationItems.map((item) => (
              <SidebarItem 
                key={item.href} 
                item={item} 
                isActive={pathname === item.href || pathname.startsWith(`${item.href}/`)}
                isCollapsed={isCollapsed}
                user={user || null}
                onClick={() => {
                  // Close mobile drawer on navigation
                  if (window.innerWidth < 768) {
                    onClose();
                  }
                }}
              />
            ))}
          </ul>
        </nav>
      </aside>
    </>
  );
}

