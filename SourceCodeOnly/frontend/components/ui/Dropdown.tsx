"use client";

import React, { useState, useRef, useEffect } from "react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface DropdownProps {
  trigger: React.ReactNode;
  children: React.ReactNode;
  align?: "left" | "right";
  className?: string;
}

export function Dropdown({ trigger, children, align = "left", className }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Close on escape key
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  return (
    <div className={cn("relative inline-block text-left", className)} ref={dropdownRef}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="true"
        aria-expanded={isOpen}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            setIsOpen(!isOpen);
          }
        }}
        className="cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-brand-500 rounded-md"
      >
        {trigger}
      </div>

      {isOpen && (
        <div
          className={cn(
            "absolute z-dropdown mt-2 w-56 rounded-md border border-border bg-surface shadow-lg ring-1 ring-black/5 animate-fade-in",
            align === "right" ? "right-0 origin-top-right" : "left-0 origin-top-left"
          )}
          role="menu"
          aria-orientation="vertical"
        >
          <div className="py-1" onClick={() => setIsOpen(false)}>
            {children}
          </div>
        </div>
      )}
    </div>
  );
}

import Link from "next/link";

interface DropdownItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: React.ReactNode;
  variant?: "default" | "danger";
  href?: string;
}

export function DropdownItem({ children, icon, variant = "default", className, href, ...props }: DropdownItemProps) {
  const content = (
    <>
      {icon && <span className="mr-3 h-4 w-4">{icon}</span>}
      {children}
    </>
  );

  const styles = cn(
    "flex w-full items-center px-4 py-2 text-sm transition-colors focus:outline-none focus:bg-background text-left",
    variant === "danger"
      ? "text-danger hover:bg-danger/10 hover:text-danger"
      : "text-foreground hover:bg-background hover:text-foreground",
    className
  );

  if (href) {
    return (
      <Link href={href} className={styles} role="menuitem">
        {content}
      </Link>
    );
  }

  return (
    <button
      type="button"
      className={styles}
      role="menuitem"
      {...props}
    >
      {content}
    </button>
  );
}
