"use client";

import { useMemo } from "react";
import { Users, ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import type { FriendRelation } from "@/lib/api-client";

const STAR_COLORS = [
  "#A78BFA", "#38BDF8", "#34D399", "#FB923C",
  "#F472B6", "#818CF8", "#FBBF24", "#67E8F9",
];

function hashColor(id: string): string {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = ((hash << 5) - hash) + id.charCodeAt(i);
    hash |= 0;
  }
  return STAR_COLORS[Math.abs(hash) % STAR_COLORS.length];
}

function StarIcon({ color, size = 36 }: { color: string; size?: number }) {
  const cx = size / 2;
  const cy = size / 2;
  const outer = size * 0.42;
  const inner = size * 0.18;
  const points: string[] = [];
  for (let i = 0; i < 5; i++) {
    const outerAngle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
    const innerAngle = outerAngle + Math.PI / 5;
    points.push(`${cx + outer * Math.cos(outerAngle)},${cy + outer * Math.sin(outerAngle)}`);
    points.push(`${cx + inner * Math.cos(innerAngle)},${cy + inner * Math.sin(innerAngle)}`);
  }
  const filterId = `star-glow-${color.replace("#", "")}`;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <defs>
        <filter id={filterId}>
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <polygon
        points={points.join(" ")}
        fill={color}
        opacity="0.85"
        filter={`url(#${filterId})`}
      />
    </svg>
  );
}

interface PeopleFreeNowProps {
  friends: FriendRelation[];
  availMap: Map<string, boolean>;
  loading: boolean;
}

export function PeopleFreeNow({ friends, availMap, loading }: PeopleFreeNowProps) {
  const freeFriends = useMemo(
    () => friends.filter((fr) => availMap.get(fr.user.id)),
    [friends, availMap],
  );

  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(139,92,246,0.03)_0%,transparent_60%)] pointer-events-none" />
      <div className="relative z-10">
        <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
          People Free Now
        </p>
        <p className="text-sm text-text-muted mb-4">Your available friends</p>

        {loading ? (
          <div className="flex gap-2.5 flex-wrap">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex flex-col items-center gap-1.5">
                <div className="w-9 h-9 bg-white/[0.04] animate-pulse" style={{ clipPath: "polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)" }} />
                <div className="h-3 w-12 bg-white/[0.04] rounded animate-pulse" />
              </div>
            ))}
          </div>
        ) : freeFriends.length === 0 ? (
          <div className="py-8 text-center">
            <Users className="w-8 h-8 text-text-muted/30 mx-auto mb-2" />
            <p className="text-sm text-text-muted">No one free right now</p>
          </div>
        ) : (
          <div className="flex gap-4 flex-wrap">
            {freeFriends.slice(0, 8).map((fr) => {
              const color = hashColor(fr.user.id);
              return (
                <div key={fr.user.id} className="flex flex-col items-center gap-1.5">
                  <StarIcon color={color} />
                  <span className="text-[10px] text-text-muted truncate max-w-[56px] text-center leading-tight">
                    {fr.user.display_name.split(" ")[0]}
                  </span>
                  <span className="w-1.5 h-1.5 rounded-full bg-status-available" />
                </div>
              );
            })}
          </div>
        )}

        <a
          href="/friends"
          className="mt-4 block text-center text-xs text-primary-400 hover:text-primary-300 transition-colors flex items-center justify-center gap-1"
        >
          View all people
          <ArrowRight className="w-3 h-3" />
        </a>
      </div>
    </Card>
  );
}
