"use client";

import { useState, useEffect, useCallback } from "react";
import { Plus, ArrowRight } from "lucide-react";
import { api, GroupSummary } from "@/lib/api-client";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CreateGroupDialog } from "@/components/groups/create-group-dialog";

interface GroupColorSet {
  star: string;
  line: string;
  glow: string;
  accentStar?: string;
}

const GROUP_COLORS: GroupColorSet[] = [
  { star: "rgba(167,139,250,0.85)", line: "rgba(139,92,246,0.40)", glow: "rgba(139,92,246,0.5)" },
  { star: "rgba(56,189,248,0.85)", line: "rgba(56,189,248,0.40)", glow: "rgba(56,189,248,0.5)" },
  { star: "rgba(251,191,36,0.85)", line: "rgba(245,158,11,0.40)", glow: "rgba(245,158,11,0.5)", accentStar: "rgba(244,114,182,0.85)" },
];

interface StarPt {
  x: number;
  y: number;
  accent?: boolean;
}

const SHAPES: StarPt[][] = [
  [{ x: 50, y: 20 }, { x: 25, y: 50 }, { x: 75, y: 50 }, { x: 50, y: 75 }],
  [{ x: 50, y: 18 }, { x: 20, y: 45 }, { x: 80, y: 45 }, { x: 50, y: 70 }, { x: 50, y: 45 }],
  [{ x: 50, y: 22 }, { x: 30, y: 58 }, { x: 70, y: 58 }],
  [{ x: 25, y: 28 }, { x: 75, y: 28 }, { x: 50, y: 55 }, { x: 25, y: 72 }, { x: 75, y: 72 }],
  [{ x: 50, y: 15 }, { x: 20, y: 40 }, { x: 80, y: 40 }, { x: 50, y: 68 }],
];

function MiniConstellation({ index }: { index: number }) {
  const shape = SHAPES[index % SHAPES.length];
  const colors = GROUP_COLORS[index % GROUP_COLORS.length];
  const filterId = `mc-glow-${index}`;

  const lines: { x1: number; y1: number; x2: number; y2: number }[] = [];
  for (let i = 0; i < shape.length - 1; i++) {
    lines.push({ x1: shape[i].x, y1: shape[i].y, x2: shape[i + 1].x, y2: shape[i + 1].y });
  }
  if (shape.length > 2) {
    lines.push({ x1: shape[shape.length - 1].x, y1: shape[shape.length - 1].y, x2: shape[0].x, y2: shape[0].y });
  }

  return (
    <svg viewBox="0 0 100 100" className="w-10 h-10 shrink-0">
      <defs>
        <filter id={filterId}>
          <feGaussianBlur stdDeviation="1.5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      {lines.map((l, i) => (
        <line key={i} {...l} stroke={colors.line} strokeWidth="0.8" />
      ))}
      {shape.map((p, i) => {
        const fill = (p.accent && colors.accentStar) ? colors.accentStar : colors.star;
        return (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="3"
            fill={fill}
            filter={`url(#${filterId})`}
          />
        );
      })}
    </svg>
  );
}

export function YourGroupsCard() {
  const [groups, setGroups] = useState<GroupSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.groups.list();
      setGroups(data.groups);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not load your groups");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(56,189,248,0.03)_0%,transparent_60%)] pointer-events-none" />
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-1">
          <p className="text-xs text-text-muted uppercase tracking-wider">
            Your Groups
          </p>
          <Button variant="ghost" size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="w-3.5 h-3.5" />
          </Button>
        </div>
        <p className="text-sm text-text-muted mb-4">Your groups at a glance</p>

        {showCreate && (
          <CreateGroupDialog
            onClose={() => setShowCreate(false)}
            onCreated={() => { setShowCreate(false); load(); }}
          />
        )}

        {loading ? (
          <div className="space-y-3">
            {[1, 2].map((i) => (
              <div key={i} className="flex items-center gap-3">
                <Skeleton className="w-10 h-10 rounded-lg" />
                <div className="flex-1 space-y-1">
                  <Skeleton className="h-4 w-28" />
                  <Skeleton className="h-3 w-16" />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="py-6 text-center">
            <p className="text-xs text-text-muted/60">{error}</p>
            <Button variant="secondary" size="sm" onClick={load} className="mt-2">
              Try again
            </Button>
          </div>
        ) : groups.length === 0 ? (
          <div className="py-6 text-center">
            <p className="text-sm text-text-muted">No groups yet</p>
            <Button variant="primary" size="sm" onClick={() => setShowCreate(true)} className="mt-3">
              <Plus className="w-3.5 h-3.5" />
              Create Group
            </Button>
          </div>
        ) : (
          <div className="space-y-2">
            {groups.slice(0, 4).map((g, idx) => (
              <a key={g.id} href={`/groups/${g.id}`}>
                <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/[0.04] transition-colors">
                  <MiniConstellation index={idx} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-text-primary truncate">{g.name}</p>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-status-available" />
                      <span className="text-xs text-text-muted">{g.member_count} free now</span>
                    </div>
                  </div>
                </div>
              </a>
            ))}
          </div>
        )}

        <a
          href="/groups"
          className="mt-3 block text-center text-xs text-primary-400 hover:text-primary-300 transition-colors flex items-center justify-center gap-1"
        >
          View all groups
          <ArrowRight className="w-3 h-3" />
        </a>
      </div>
    </Card>
  );
}
