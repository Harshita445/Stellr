"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Star,
  Users,
  Clock,
  Sparkles,
  Calendar,
} from "lucide-react";
import { api, FriendRelation, DashboardResponse } from "@/lib/api-client";
import { VisibleStars } from "@/components/dashboard/visible-stars";
import { Constellations } from "@/components/dashboard/constellations";

interface Stats {
  friendCount: number;
  groupCount: number;
  isFree: boolean;
  nextWindow: string | null;
  nextWindowDuration: number | null;
}

function useStats() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [friendsData, groupsData, dashData] = await Promise.all([
        api.friends.list(),
        api.groups.list(),
        api.dashboard.get(),
      ]);
      setStats({
        friendCount: friendsData.friends.length,
        groupCount: groupsData.groups.length,
        isFree: !dashData.current_class,
        nextWindow:
          dashData.free_windows.length > 0
            ? dashData.free_windows[0].start_time
            : null,
        nextWindowDuration:
          dashData.free_windows.length > 0
            ? dashData.free_windows[0].duration_minutes
            : null,
      });
    } catch {
      // children handle their own errors
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return { stats, loading };
}

function StatChip({
  icon: Icon,
  label,
  value,
  loading,
  accent,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  loading?: boolean;
  accent?: string;
}) {
  return (
    <div
      className={`flex items-center gap-3 px-4 py-2.5 rounded-xl glass border ${
        accent
          ? `border-${accent}/20`
          : "border-glass-border"
      }`}
    >
      <Icon className={`w-4 h-4 ${accent ? `text-${accent}` : "text-text-muted"}`} />
      <div className="min-w-0">
        <p className="text-xs text-text-muted leading-tight">{label}</p>
        {loading ? (
          <div className="h-4 w-16 bg-space-400/30 rounded mt-0.5 animate-pulse" />
        ) : (
          <p className="text-sm font-semibold text-text-primary truncate">
            {value}
          </p>
        )}
      </div>
    </div>
  );
}

const staggerItem = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0 },
};

export default function DashboardPage() {
  const { stats, loading } = useStats();

  return (
    <main className="min-h-screen p-4 md:p-6 lg:p-8 max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="space-y-5 md:space-y-6"
      >
        {/* ── Header ─────────────────────────────────────────────── */}
        <motion.div variants={staggerItem} className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-primary-500/15 flex items-center justify-center shrink-0">
            <Sparkles className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-text-primary tracking-tight">
              Stellr
            </h1>
            <p className="text-xs md:text-sm text-text-muted leading-snug">
              Your people. Your time. Aligned.
            </p>
          </div>
        </motion.div>

        {/* ── Quick-glance Stats Strip ───────────────────────────── */}
        <motion.div
          variants={staggerItem}
          className="flex flex-wrap gap-3"
        >
          <StatChip
            icon={Clock}
            label="Status"
            value={stats ? (stats.isFree ? "Free" : "In class") : "—"}
            loading={loading}
            accent={stats?.isFree ? "status-available" : "status-busy"}
          />
          <StatChip
            icon={Star}
            label="Your People"
            value={stats ? `${stats.friendCount}` : "—"}
            loading={loading}
          />
          <StatChip
            icon={Users}
            label="Your Groups"
            value={stats ? `${stats.groupCount}` : "—"}
            loading={loading}
          />
          <StatChip
            icon={Calendar}
            label="Next window"
            value={
              stats
                ? stats.nextWindow
                  ? `${stats.nextWindow} (${stats.nextWindowDuration}m)`
                  : "None today"
                : "—"
            }
            loading={loading}
          />
        </motion.div>

        {/* ── Cards Grid ─────────────────────────────────────────── */}
        <motion.div
          variants={staggerItem}
          className="grid grid-cols-1 lg:grid-cols-2 gap-5 md:gap-6"
        >
          <motion.div
            initial="hidden"
            animate="show"
            variants={{
              hidden: { opacity: 0, y: 12 },
              show: { opacity: 1, y: 0, transition: { delay: 0.15, duration: 0.35 } },
            }}
          >
            <VisibleStars />
          </motion.div>
          <motion.div
            initial="hidden"
            animate="show"
            variants={{
              hidden: { opacity: 0, y: 12 },
              show: { opacity: 1, y: 0, transition: { delay: 0.25, duration: 0.35 } },
            }}
          >
            <Constellations />
          </motion.div>
        </motion.div>
      </motion.div>
    </main>
  );
}
