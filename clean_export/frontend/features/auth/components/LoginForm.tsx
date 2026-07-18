"use client";

import { useState, useContext } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AuthContext } from "@/lib/contexts/AuthContext";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export default function LoginForm() {
  const { login } = useContext(AuthContext);
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") ?? "/dashboard";
  
  // Sanitize nextPath — only allow relative paths
  const safeNextPath = nextPath.startsWith("/") && !nextPath.startsWith("//") ? nextPath : "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsPending(true);
    setError(null);
    try {
      await login({ email, password });
      router.replace(safeNextPath);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Invalid email or password"));
      setIsPending(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5 w-full max-w-sm mx-auto">
      <div className="text-center mb-2">
        <h1 className="text-2xl font-bold text-foreground">Welcome back</h1>
        <p className="text-sm text-muted mt-1">Sign in to your account</p>
      </div>

      {error && (
        <div className="p-3 bg-danger/10 border border-danger/20 text-danger text-sm rounded-md animate-fade-in" role="alert">
          {error.message}
        </div>
      )}

      <div className="flex flex-col gap-1.5">
        <label htmlFor="email" className="text-sm font-medium text-foreground">Email</label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={isPending}
          placeholder="name@example.com"
          autoComplete="email"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <div className="flex justify-between items-center">
          <label htmlFor="password" className="text-sm font-medium text-foreground">Password</label>
          <a href="#" className="text-sm text-brand-500 hover:text-brand-600 font-medium" tabIndex={-1}>
            Forgot password?
          </a>
        </div>
        <Input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          disabled={isPending}
          autoComplete="current-password"
        />
      </div>

      <div className="flex items-center gap-2">
        <input 
          type="checkbox" 
          id="remember" 
          className="rounded border-border text-brand-500 focus:ring-brand-500 h-4 w-4 bg-background"
        />
        <label htmlFor="remember" className="text-sm text-foreground cursor-pointer">
          Remember me for 30 days
        </label>
      </div>

      <Button
        type="submit"
        isLoading={isPending}
        className="mt-2 w-full"
      >
        Sign In
      </Button>
    </form>
  );
}
