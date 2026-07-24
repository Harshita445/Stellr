"use client";

import { Clock, Users, ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import type { GroupMember, MemberAvailability } from "@/lib/api-client";

interface NextAlignmentCardProps {
  groupName?: string;
  startTime?: string;
  endTime?: string;
  memberCount?: number;
  freeCount?: number;
  members?: GroupMember[];
  memberAvailabilities?: MemberAvailability[];
}

const decoStars = [
  { cx: 38, cy: 30, r: 5 },
  { cx: 72, cy: 18, r: 4 },
  { cx: 85, cy: 52, r: 6 },
  { cx: 55, cy: 65, r: 4.5 },
  { cx: 30, cy: 58, r: 3.5 },
];

const decoLines: [number, number][] = [
  [0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [0, 2],
];

export function NextAlignmentCard({
  groupName = "Study Group",
  startTime = "15:00",
  endTime = "17:00",
  memberCount = 4,
  freeCount = 3,
}: NextAlignmentCardProps) {
  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_right,rgba(139,92,246,0.10)_0%,transparent_70%)] pointer-events-none" />
      <div className="relative z-10">
        <p className="text-xs text-text-muted uppercase tracking-wider mb-3">
          Next Alignment
        </p>

        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-primary-400 shrink-0" />
              <span className="text-xl font-bold text-text-primary">
                {startTime} – {endTime}
              </span>
            </div>
            <p className="text-xs text-text-muted mb-1">
              2h · {freeCount}/{memberCount} free
            </p>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-status-available" />
              <span className="text-xs text-status-available font-medium">
                {freeCount === memberCount ? "Everyone is free" : `${freeCount} members free`}
              </span>
            </div>
          </div>

          {/* Decorative constellation — static SVG */}
          <div className="shrink-0 w-24 h-24">
            <svg viewBox="0 0 100 80" className="w-full h-full">
              <defs>
                <filter id="deco-glow">
                  <feGaussianBlur stdDeviation="2" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>
              {decoLines.map(([i, j], idx) => (
                <line
                  key={idx}
                  x1={decoStars[i].cx}
                  y1={decoStars[i].cy}
                  x2={decoStars[j].cx}
                  y2={decoStars[j].cy}
                  stroke="rgba(139,92,246,0.40)"
                  strokeWidth="1"
                />
              ))}
              {decoStars.map((s, i) => (
                <circle
                  key={i}
                  cx={s.cx}
                  cy={s.cy}
                  r={s.r}
                  fill="rgba(167,139,250,0.8)"
                  filter="url(#deco-glow)"
                />
              ))}
            </svg>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="w-3.5 h-3.5 text-text-muted" />
            <span className="text-sm text-text-primary font-medium truncate max-w-[140px]">
              {groupName}
            </span>
            <span className="text-xs text-text-muted">
              {freeCount} free
            </span>
          </div>
          <a
            href="/groups"
            className="text-xs text-primary-400 hover:text-primary-300 transition-colors flex items-center gap-1"
          >
            View details
            <ArrowRight className="w-3 h-3" />
          </a>
        </div>
      </div>
    </Card>
  );
}
