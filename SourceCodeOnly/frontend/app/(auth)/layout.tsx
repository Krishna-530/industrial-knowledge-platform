"use client";

import { useContext, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthContext } from "@/lib/contexts/AuthContext";
import Loading from "@/app/loading";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const { status } = useContext(AuthContext);
  const router = useRouter();

  useEffect(() => {
    if (status === "authenticated") {
      router.replace("/dashboard");
    }
  }, [status, router]);

  if (status === "initializing" || status === "restoring" || status === "hydrating" || status === "authenticated") {
    return <Loading />;
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4 text-foreground">
      <div className="w-full max-w-md bg-surface p-8 rounded-xl shadow-md border border-border">
        {children}
      </div>
    </div>
  );
}
