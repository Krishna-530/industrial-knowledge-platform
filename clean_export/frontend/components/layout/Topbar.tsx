"use client";

import { useContext } from "react";
import { ThemeContext } from "@/lib/contexts/ThemeContext";
import { SunIcon, MoonIcon, MonitorIcon, LogOutIcon, SearchIcon, MenuIcon, SettingsIcon, UserIcon } from "@/lib/icons";
import { AuthContext } from "@/lib/contexts/AuthContext";
import { useCurrentUser } from "@/features/auth/hooks";
import { Avatar } from "@/components/ui/Avatar";
import { Dropdown, DropdownItem } from "@/components/ui/Dropdown";
import { Input } from "@/components/ui/Input";
import Link from "next/link";

interface TopbarProps {
  onMenuToggle: () => void;
}

export default function Topbar({ onMenuToggle }: TopbarProps) {
  const { mode, setMode } = useContext(ThemeContext);
  const { data: user } = useCurrentUser();
  const { logout } = useContext(AuthContext);

  const cycleTheme = () => {
    if (mode === "system") setMode("light");
    else if (mode === "light") setMode("dark");
    else setMode("system");
  };

  return (
    <header className="h-16 flex-shrink-0 border-b border-border bg-surface flex items-center px-4 justify-between z-10">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuToggle}
          className="md:hidden p-2 -ml-2 text-muted hover:text-foreground rounded-md focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
          aria-label="Toggle menu"
        >
          <MenuIcon className="h-6 w-6" />
        </button>
        <div className="font-semibold text-foreground md:hidden">Platform</div>
      </div>
      
      <div className="hidden md:flex flex-1 max-w-md ml-4 relative">
        {/* Search Placeholder */}
        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
        <Input 
          className="pl-9 bg-background/50" 
          placeholder="Search... (Placeholder)"
          readOnly
        />
      </div>

      <div className="ml-auto flex items-center gap-2 md:gap-4 pl-4">
        {/* Theme Toggle */}
        <button
          onClick={cycleTheme}
          className="p-2 text-muted hover:text-foreground hover:bg-background rounded-md transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
          title={`Theme: ${mode}`}
        >
          {mode === "light" && <SunIcon className="h-5 w-5" />}
          {mode === "dark" && <MoonIcon className="h-5 w-5" />}
          {mode === "system" && <MonitorIcon className="h-5 w-5" />}
        </button>

        <div className="h-6 w-px bg-border hidden sm:block mx-1"></div>

        {/* Profile Dropdown */}
        <Dropdown
          align="right"
          trigger={
            <div className="flex items-center gap-3 hover:bg-background p-1 pr-2 rounded-full transition-colors">
              <Avatar name={user?.name} />
              <div className="hidden sm:flex flex-col items-start">
                <span className="text-sm font-medium text-foreground leading-none">{user?.name || "User"}</span>
                <span className="text-xs text-muted leading-none mt-1">{user?.roles?.[0] || "Member"}</span>
              </div>
            </div>
          }
        >
          <div className="px-4 py-3 border-b border-border mb-1">
            <p className="text-sm font-medium text-foreground">{user?.name}</p>
            <p className="text-xs text-muted truncate">{user?.email}</p>
          </div>
          <DropdownItem href="/profile" icon={<UserIcon />}>Profile</DropdownItem>
          <DropdownItem href="/settings" icon={<SettingsIcon />}>Settings</DropdownItem>
          
          <div className="h-px bg-border my-1"></div>
          
          <DropdownItem 
            icon={<LogOutIcon />} 
            variant="danger" 
            onClick={() => logout()}
          >
            Log out
          </DropdownItem>
        </Dropdown>
      </div>
    </header>
  );
}
