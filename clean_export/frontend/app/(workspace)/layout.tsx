"use client";

import { useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { AuthContext } from "@/lib/contexts/AuthContext";
import LoadingOverlay from "@/components/feedback/LoadingOverlay";
import Sidebar from "@/components/layout/Sidebar";
import Topbar from "@/components/layout/Topbar";
import ContentArea from "@/components/layout/ContentArea";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const { status } = useContext(AuthContext);
  const router = useRouter();
  const pathname = usePathname();

  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (status === "unauthenticated" || status === "authenticating") {
      // Safe redirect parameter — restrict to relative paths only
      const isRelative = pathname.startsWith("/") && !pathname.startsWith("//");
      const nextParam = encodeURIComponent(isRelative ? pathname : "/dashboard");
      router.replace(`/login?next=${nextParam}`);
    }
  }, [status, pathname, router]);

  if (status === "initializing" || status === "restoring" || status === "hydrating") {
    // Full screen loading overlay while session restore is in progress
    return <LoadingOverlay />;
  }

  if (status === "unauthenticated" || status === "authenticating") {
    // We are redirecting
    return null;
  }

  // AUTHENTICATED
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar isMobileOpen={isMobileMenuOpen} onClose={() => setIsMobileMenuOpen(false)} />

      <div className="flex-1 flex flex-col overflow-hidden relative">
        <Topbar onMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)} />
        
        <ContentArea>
          {children}
        </ContentArea>
      </div>
    </div>
  );
}

