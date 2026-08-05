"use client";

import { Clock, ArrowRight, Star } from "lucide-react";
import { Card } from "@/components/ui/card";
import type { DashboardFreeWindow } from "@/lib/api-client";

interface TodaysWindowsProps {
  windows: DashboardFreeWindow[];
  loading: boolean;
}

export function TodaysWindows({ windows, loading }: TodaysWindowsProps) {
  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(56,189,248,0.03)_0%,transparent_60%)] pointer-events-none" />
      <div className="relative z-10">
        <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
          Today's Windows
        </p>
        <p className="text-sm text-text-muted mb-4">Your free time today</p>

        {loading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div key={i} className="h-12 bg-white/[0.04] rounded-lg animate-pulse" />
            ))}
          </div>
        ) : windows.length === 0 ? (
          <div className="py-8 text-center">
            <Clock className="w-8 h-8 text-text-muted/30 mx-auto mb-2" />
            <p className="text-sm text-text-muted">No free windows today</p>
          </div>
        ) : (
          <div className="space-y-1.5">
            {windows.map((w, i) => {
              const isHighlighted = i === 0;
              return (
                <div
                  key={i}
                  className={`relative flex items-center gap-3 p-2.5 rounded-lg ${
                    isHighlighted
                      ? "bg-primary-500/10 border-l-[3px] border-primary-400"
                      : "hover:bg-white/[0.03]"
                  }`}
                >
                  {isHighlighted && (
                    <div className="absolute top-1.5 right-1.5">
                      <Star className="w-3 h-3 text-primary-400 fill-primary-400/40" />
                    </div>
                  )}
                  <Clock className="w-3.5 h-3.5 text-text-muted shrink-0" />
                  <span className="text-sm text-text-primary font-medium flex-1">
                    {w.start_time} – {w.end_time}
                  </span>
                  <span className="text-xs text-text-muted">{w.duration_minutes}m</span>
                </div>
              );
            })}
          </div>
        )}

        <a
          href="#"
          className="mt-3 block text-center text-xs text-primary-400 hover:text-primary-300 transition-colors flex items-center justify-center gap-1"
        >
          View full schedule
          <ArrowRight className="w-3 h-3" />
        </a>
      </div>
    </Card>
  );
}
