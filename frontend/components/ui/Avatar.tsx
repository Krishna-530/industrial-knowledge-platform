import React from "react";
import { UserIcon } from "@/lib/icons";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export interface AvatarProps {
  name?: string | null;
  className?: string;
}

export function Avatar({ name, className }: AvatarProps) {
  const initial = name ? name.charAt(0).toUpperCase() : "";

  return (
    <div
      className={cn(
        "flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-brand-700 font-bold overflow-hidden flex-shrink-0",
        className
      )}
      aria-hidden="true"
    >
      {initial ? initial : <UserIcon className="h-4 w-4" />}
    </div>
  );
}
