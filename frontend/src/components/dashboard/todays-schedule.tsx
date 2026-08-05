"use client";

import { ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { DashboardScheduleItem } from "@/lib/api-client";

interface TodaysScheduleProps {
  schedule: DashboardScheduleItem[];
  loading: boolean;
}

function ScheduleRow({ item, isFree }: { item: DashboardScheduleItem; isFree?: boolean }) {
  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-white/[0.04] last:border-0">
      <div className="flex flex-col items-center gap-0.5">
        <div className={`w-2 h-2 rounded-full ${isFree ? "bg-status-available" : "bg-status-busy"}`} />
        <div className="w-px h-6 bg-white/[0.10]" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs text-text-muted">
          {item.start_time} – {item.end_time}
        </p>
        <p className={`text-sm font-medium truncate ${
          isFree ? "text-status-available" : "text-text-primary"
        }`}>
          {isFree ? "Free" : `${item.course_code} — ${item.course_name}`}
        </p>
      </div>
      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
        isFree
          ? "bg-status-available/10 text-status-available"
          : "bg-status-busy/10 text-status-busy"
      }`}>
        {isFree ? "Free" : "Class"}
      </span>
    </div>
  );
}

export function TodaysSchedule({ schedule, loading }: TodaysScheduleProps) {
  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(139,92,246,0.03)_0%,transparent_60%)] pointer-events-none" />
      <div className="relative z-10">
        <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
          Today's Schedule
        </p>
        <p className="text-sm text-text-muted mb-4">Your day at a glance</p>

        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-14 w-full rounded-lg" />
            ))}
          </div>
        ) : schedule.length === 0 ? (
          <div className="py-8 text-center">
            <p className="text-sm text-text-muted">No classes today</p>
            <p className="text-xs text-text-muted/50 mt-1">Enjoy your free day</p>
          </div>
        ) : (
          schedule.map((item, i) => (
            <ScheduleRow key={i} item={item} />
          ))
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
