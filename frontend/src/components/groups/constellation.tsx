"use client";

import { useState, useMemo, useCallback, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { GroupMember, MemberAvailability } from "@/lib/api-client";

interface ConstellationProps {
  members: GroupMember[];
  memberAvailabilities: MemberAvailability[];
  onMemberClick?: (userId: string) => void;
  className?: string;
  compact?: boolean;
}

interface StarPos {
  x: number;
  y: number;
}

type ConstellationState = "none" | "alone" | "connected" | "partial" | "full";

const STAR_SIZE = 32;

function computePositions(count: number, w: number, h: number): StarPos[] {
  const cx = w / 2;
  const cy = h / 2;
  const r = Math.min(w, h) * 0.38;

  if (count === 0) return [];
  if (count === 1) return [{ x: cx, y: cy }];
  if (count === 2)
    return [
      { x: cx - r * 0.5, y: cy },
      { x: cx + r * 0.5, y: cy },
    ];

  if (count === 7) {
    const pts: StarPos[] = [];
    for (let i = 0; i < 6; i++) {
      const a = (i * 2 * Math.PI) / 6 - Math.PI / 2;
      pts.push({ x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) });
    }
    pts.push({ x: cx, y: cy });
    return pts;
  }

  if (count === 8) {
    const spacing = (w * 0.55) / 3;
    const startX = cx - spacing * 1.5;
    const topY = cy - r * 0.45;
    const botY = cy + r * 0.45;
    const pts: StarPos[] = [];
    for (let i = 0; i < 4; i++) pts.push({ x: startX + spacing * i, y: topY });
    for (let i = 0; i < 4; i++) pts.push({ x: startX + spacing * i, y: botY });
    return pts;
  }

  const pts: StarPos[] = [];
  for (let i = 0; i < count; i++) {
    const a = (i * 2 * Math.PI) / count - Math.PI / 2;
    pts.push({ x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) });
  }
  return pts;
}

function deriveState(freeCount: number, total: number): ConstellationState {
  if (freeCount === 0) return "none";
  if (freeCount === 1) return "alone";
  if (freeCount === 2) return "connected";
  if (freeCount === total) return "full";
  return "partial";
}

function computeLines(
  freeIndices: number[],
  total: number,
  state: ConstellationState,
): [number, number][] {
  if (state === "connected" && freeIndices.length === 2) {
    return [[freeIndices[0], freeIndices[1]]];
  }
  if (state === "partial") {
    const lines: [number, number][] = [];
    for (let i = 0; i < freeIndices.length; i++) {
      for (let j = i + 1; j < freeIndices.length; j++) {
        const dist = Math.min(
          Math.abs(freeIndices[i] - freeIndices[j]),
          total - Math.abs(freeIndices[i] - freeIndices[j]),
        );
        if (dist <= 2) {
          lines.push([freeIndices[i], freeIndices[j]]);
        }
      }
    }
    return lines;
  }
  if (state === "full") {
    const lines: [number, number][] = [];
    for (let i = 0; i < total; i++) {
      for (let j = i + 1; j < total; j++) {
        lines.push([i, j]);
      }
    }
    return lines;
  }
  return [];
}

function StateDescription({
  state,
  freeMembers,
  total,
}: {
  state: ConstellationState;
  freeMembers: MemberAvailability[];
  total: number;
}) {
  const text = useMemo(() => {
    switch (state) {
      case "none":
        return "No one is free right now";
      case "alone":
        return `${freeMembers[0]?.display_name ?? "Someone"} is free`;
      case "connected":
        return `${freeMembers[0]?.display_name ?? "Someone"} and ${freeMembers[1]?.display_name ?? "someone else"} are free`;
      case "partial":
        return `${freeMembers.length} of ${total} are free`;
      case "full":
        return "Everyone is free!";
    }
  }, [state, freeMembers, total]);
  return (
    <motion.p
      className="absolute bottom-2 left-0 right-0 text-center text-xs text-text-secondary pointer-events-none"
      key={text}
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {text}
    </motion.p>
  );
}

export function Constellation({
  members,
  memberAvailabilities,
  onMemberClick,
  className = "",
  compact = false,
}: ConstellationProps) {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ w: 300, h: 300 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        if (width > 0 && height > 0) {
          setSize({ w: width, h: height });
        }
      }
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const positions = useMemo(
    () => computePositions(members.length, size.w, size.h),
    [members.length, size.w, size.h],
  );

  const availByUserId = useMemo(() => {
    const map = new Map<string, boolean>();
    for (const a of memberAvailabilities) {
      map.set(a.user_id, a.is_free_now);
    }
    return map;
  }, [memberAvailabilities]);

  const freeIndices = useMemo(() => {
    const indices: number[] = [];
    members.forEach((m, i) => {
      if (availByUserId.get(m.user_id)) indices.push(i);
    });
    return indices;
  }, [members, availByUserId]);

  const state = deriveState(freeIndices.length, members.length);

  const lines = useMemo(
    () => computeLines(freeIndices, members.length, state),
    [freeIndices, members.length, state],
  );

  const freeMembers = useMemo(
    () => memberAvailabilities.filter((a) => a.is_free_now),
    [memberAvailabilities],
  );

  const handleStarClick = useCallback(
    (userId: string) => {
      if (onMemberClick) {
        onMemberClick(userId);
      } else {
        router.push(`/friends?compare=${userId}`);
      }
    },
    [onMemberClick, router],
  );

  const pauseAnimations = freeIndices.length === 0;

  return (
    <div
      ref={containerRef}
      className={`relative overflow-hidden ${className}`}
      style={{ minHeight: compact ? 120 : 200, width: "100%" }}
      role="img"
      aria-label={`Constellation — ${freeMembers.length} of ${members.length} members free`}
    >
      <div
        className={`absolute inset-0 rounded-full blur-3xl transition-opacity duration-700 pointer-events-none ${
          state === "full"
            ? "opacity-60 bg-accent-500/10"
            : state === "partial"
              ? "opacity-30 bg-accent-500/5"
              : "opacity-0"
        }`}
      />

      <AnimatePresence mode="sync">
        {state === "full" && (
          <motion.div
            className="absolute inset-0 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.15, 0] }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        )}
      </AnimatePresence>

      <svg
        className="absolute inset-0 w-full h-full pointer-events-none"
        style={{ mixBlendMode: "screen" }}
      >
        <AnimatePresence mode="sync">
          {lines.map(([i, j], idx) => {
            const p1 = positions[i];
            const p2 = positions[j];
            if (!p1 || !p2) return null;
            const midX = (p1.x + p2.x) / 2;
            const midY = (p1.y + p2.y) / 2 - 4;
            return (
              <motion.path
                key={`line-${Math.min(i, j)}-${Math.max(i, j)}`}
                d={`M${p1.x},${p1.y} Q${midX},${midY} ${p2.x},${p2.y}`}
                fill="none"
                stroke="rgba(56, 189, 248, 0.6)"
                strokeWidth={state === "full" ? 2 : 1.5}
                strokeLinecap="round"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                exit={{ pathLength: 0, opacity: 0 }}
                transition={{
                  pathLength: {
                    duration: 0.8,
                    delay: idx * 0.05,
                    ease: [0.4, 0, 0.2, 1],
                  },
                  opacity: {
                    duration: 0.4,
                    delay: idx * 0.05,
                  },
                }}
                style={{
                  filter: "drop-shadow(0 0 6px rgba(56, 189, 248, 0.4))",
                }}
              />
            );
          })}
        </AnimatePresence>
      </svg>

      <AnimatePresence mode="popLayout">
        {members.map((member, i) => {
          const pos = positions[i];
          if (!pos) return null;
          const isFree = availByUserId.get(member.user_id) ?? false;

          return (
            <div
              key={member.user_id}
              className="absolute"
              style={{
                left: pos.x,
                top: pos.y,
                transform: "translate(-50%, -50%)",
              }}
            >
              <motion.button
                className="flex items-center justify-center rounded-full font-semibold cursor-pointer select-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-400"
                style={{
                  width: STAR_SIZE,
                  height: STAR_SIZE,
                }}
                initial={{ opacity: 0, scale: 0 }}
                animate={{
                  opacity: 1,
                  scale: 1,
                  backgroundColor: isFree
                    ? "rgba(34, 197, 94, 0.25)"
                    : "rgba(45, 61, 107, 0.4)",
                  border: isFree
                    ? "2px solid rgba(34, 197, 94, 0.8)"
                    : "2px solid rgba(45, 61, 107, 0.6)",
                  boxShadow: isFree
                    ? "0 0 12px rgba(34, 197, 94, 0.5)"
                    : "0 0 0px rgba(0, 0, 0, 0)",
                }}
                exit={{ opacity: 0, scale: 0 }}
                transition={{
                  opacity: { duration: 0.3, delay: i * 0.08 },
                  scale: { duration: 0.3, delay: i * 0.08, ease: "backOut" },
                  backgroundColor: { duration: 0.5 },
                  border: { duration: 0.5 },
                  boxShadow: { duration: 0.5 },
                }}
                whileHover={{
                  scale: 1.3,
                  transition: { duration: 0.15 },
                }}
                whileTap={{ scale: 0.9 }}
                onClick={() => handleStarClick(member.user_id)}
                aria-label={`${member.display_name} — ${isFree ? "free" : "busy"}`}
                role="button"
              >
                <motion.span
                  className={`text-xs font-bold ${
                    isFree ? "text-status-available" : "text-space-300"
                  }`}
                  animate={
                    isFree && !pauseAnimations
                      ? {
                          textShadow: [
                            "0 0 4px rgba(34, 197, 94, 0.3)",
                            "0 0 12px rgba(34, 197, 94, 0.6)",
                            "0 0 4px rgba(34, 197, 94, 0.3)",
                          ],
                        }
                      : { textShadow: "0 0 0px rgba(0,0,0,0)" }
                  }
                  transition={
                    isFree && !pauseAnimations
                      ? {
                          duration: 2,
                          repeat: Infinity,
                          ease: "easeInOut",
                          delay: i * 0.3,
                        }
                      : undefined
                  }
                >
                  {member.display_name.charAt(0).toUpperCase()}
                </motion.span>
              </motion.button>
            </div>
          );
        })}
      </AnimatePresence>

      {!compact && (
        <StateDescription
          state={state}
          freeMembers={freeMembers}
          total={members.length}
        />
      )}
    </div>
  );
}
