"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { api, FriendRelation, DashboardResponse } from "@/lib/api-client";
import { TopBar } from "@/components/dashboard/top-bar";
import { StatChips } from "@/components/dashboard/stat-chips";
import { NextAlignmentCard } from "@/components/dashboard/next-alignment-card";
import { YourGroupsCard } from "@/components/dashboard/your-groups-card";
import { PeopleFreeNow } from "@/components/dashboard/people-free-now";
import { TodaysWindows } from "@/components/dashboard/todays-windows";
import { TodaysSchedule } from "@/components/dashboard/todays-schedule";

const stagger = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35 } },
};

export default function DashboardPage() {
  const [dashData, setDashData] = useState<DashboardResponse | null>(null);
  const [dashLoading, setDashLoading] = useState(true);
  const [friends, setFriends] = useState<FriendRelation[]>([]);
  const [friendsLoading, setFriendsLoading] = useState(true);
  const [availMap, setAvailMap] = useState<Map<string, boolean>>(new Map());

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await api.dashboard.get();
        if (!cancelled) setDashData(data);
      } catch { /* styled error state */ } finally {
        if (!cancelled) setDashLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadFriends() {
      try {
        const data = await api.friends.list();
        if (!cancelled) setFriends(data.friends);
      } catch { /* styled empty state */ } finally {
        if (!cancelled) setFriendsLoading(false);
      }
    }
    loadFriends();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (friends.length === 0) return;
    let cancelled = false;
    async function loadAvail() {
      const map = new Map<string, boolean>();
      const results = await Promise.allSettled(
        friends.map((fr) => api.availability.compareFriend(fr.user.id)),
      );
      friends.forEach((fr, i) => {
        map.set(fr.user.id, results[i].status === "fulfilled" ? results[i].value.current_overlap : false);
      });
      if (!cancelled) setAvailMap(map);
    }
    loadAvail();
    const interval = setInterval(loadAvail, 60000);
    return () => { cancelled = true; clearInterval(interval); };
  }, [friends]);

  const freeWindows = dashData?.free_windows ?? [];
  const schedule = dashData?.today_schedule ?? [];
  const displayName = null;

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={{
        hidden: { opacity: 0 },
        show: { opacity: 1, transition: { staggerChildren: 0.08 } },
      }}
      className="space-y-6 max-w-7xl"
    >
      {/* Top Bar */}
      <motion.div variants={stagger}>
        <TopBar displayName={displayName} />
      </motion.div>

      {/* Stat Chips */}
      <motion.div variants={stagger}>
        <StatChips />
      </motion.div>

      {/* Primary Row: Next Alignment (60%) + Your Groups (40%) */}
      <motion.div variants={stagger} className="grid grid-cols-1 lg:grid-cols-5 gap-5">
        <div className="lg:col-span-3">
          <NextAlignmentCard
            members={[]}
            memberAvailabilities={[]}
          />
        </div>
        <div className="lg:col-span-2">
          <YourGroupsCard />
        </div>
      </motion.div>

      {/* Secondary Row: 3 equal cards */}
      <motion.div variants={stagger} className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <PeopleFreeNow
          friends={friends}
          availMap={availMap}
          loading={friendsLoading}
        />
        <TodaysWindows
          windows={freeWindows}
          loading={dashLoading}
        />
        <TodaysSchedule
          schedule={schedule}
          loading={dashLoading}
        />
      </motion.div>
    </motion.div>
  );
}
