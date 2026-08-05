"use client";

import { Bell, Settings, Sparkles } from "lucide-react";

function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

interface TopBarProps {
  displayName?: string | null;
}

export function TopBar({ displayName }: TopBarProps) {
  const greeting = getGreeting();

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-xl md:text-2xl font-bold text-text-primary tracking-tight flex items-center gap-2.5">
          <Sparkles className="w-5 h-5 text-primary-400" />
          {greeting}, {displayName || "there"}
        </h1>
        <p className="text-sm text-text-muted mt-0.5 ml-8">
          Your people. Your time. Aligned.
        </p>
      </div>
      <div className="flex items-center gap-3">
        <button
          className="relative w-9 h-9 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] flex items-center justify-center transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4 text-text-muted" />
          <span className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-status-available" />
        </button>
        <button
          className="w-9 h-9 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] flex items-center justify-center transition-colors"
          aria-label="Settings"
        >
          <Settings className="w-4 h-4 text-text-muted" />
        </button>
      </div>
    </div>
  );
}
