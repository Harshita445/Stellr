"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Home,
  Users,
  Layers,
  Calendar,
  GitBranch,
  Moon,
  Sparkles,
  Copy,
  Check,
} from "lucide-react";
import { api } from "@/lib/api-client";

const navItems = [
  { href: "/dashboard", label: "Home", icon: Home },
  { href: "/friends", label: "People", icon: Users },
  { href: "/groups", label: "Groups", icon: Layers },
  { href: "#", label: "Schedule", icon: Calendar, disabled: true },
  { href: "#", label: "Alignments", icon: GitBranch, disabled: true },
];

const starPositions = [
  { x: 36, y: 60, r: 2.5, opacity: 0.5 },
  { x: 80, y: 90, r: 2, opacity: 0.4 },
  { x: 120, y: 50, r: 1.5, opacity: 0.35 },
  { x: 160, y: 100, r: 2, opacity: 0.45 },
  { x: 50, y: 130, r: 1.5, opacity: 0.3 },
  { x: 140, y: 150, r: 2.5, opacity: 0.5 },
  { x: 100, y: 180, r: 1.5, opacity: 0.35 },
  { x: 70, y: 210, r: 2, opacity: 0.4 },
  { x: 160, y: 220, r: 2, opacity: 0.3 },
  { x: 40, y: 250, r: 1.5, opacity: 0.35 },
];

const connections = [
  [0, 1], [1, 2], [2, 3], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [4, 8], [5, 9],
];

export function Sidebar() {
  const pathname = usePathname();
  const [stellrCode, setStellrCode] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api.users.me()
      .then((p) => setStellrCode(p.stellr_code))
      .catch(() => {});
  }, []);

  const handleCopy = async () => {
    if (!stellrCode) return;
    try {
      await navigator.clipboard.writeText(stellrCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {}
  };

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 z-30 flex flex-col bg-space-800/80 backdrop-blur-xl border-r border-white/[0.06]">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 pt-6 pb-5 border-b border-white/[0.06]">
        <img
          src="/Screenshot%20from%202026-07-24%2013-10-31.png"
          alt="Stellr"
          className="w-8 h-8 shrink-0"
        />
        <span className="text-lg font-bold text-text-primary tracking-tight">
          Stellr
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 pt-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.label}
              href={item.disabled ? "#" : item.href}
              className={`relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                item.disabled
                  ? "text-text-muted/40 cursor-not-allowed"
                  : isActive
                    ? "text-text-primary bg-primary-500/12"
                    : "text-text-muted hover:text-text-secondary hover:bg-white/[0.04]"
              }`}
              onClick={(e) => { if (item.disabled) e.preventDefault(); }}
            >
              {isActive && (
                <motion.div
                  layoutId="nav-accent"
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r bg-primary-400"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              <Icon className="w-4 h-4 shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Decorative constellation */}
      <div className="relative h-32 mx-4 mb-4 rounded-xl overflow-hidden">
        <svg viewBox="0 0 200 280" className="w-full h-full opacity-60">
          {connections.map(([i, j]) => (
            <line
              key={`line-${i}-${j}`}
              x1={starPositions[i].x}
              y1={starPositions[i].y}
              x2={starPositions[j].x}
              y2={starPositions[j].y}
              stroke="rgba(139,92,246,0.2)"
              strokeWidth="0.5"
            />
          ))}
          {starPositions.map((s, i) => (
            <circle
              key={i}
              cx={s.x}
              cy={s.y}
              r={s.r}
              fill="rgba(167,139,250,0.6)"
            />
          ))}
        </svg>
      </div>

      {/* Dark Sky toggle */}
      <div className="px-4 mb-3">
        <button
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-text-muted bg-white/[0.03] hover:bg-white/[0.06] transition-colors border border-white/[0.04] cursor-default"
          onClick={(e) => e.preventDefault()}
        >
          <Moon className="w-3.5 h-3.5 text-primary-400/60" />
          <span>Dark Sky</span>
          <span className="ml-auto opacity-40">v1.0</span>
        </button>
      </div>

      {/* Profile section — Stellr code */}
      {stellrCode && (
        <div className="mx-4 mb-2 px-3.5 py-2.5 rounded-xl bg-space-700/50 border border-white/[0.04]">
          <p className="text-[10px] text-text-muted/60 uppercase tracking-wider mb-1.5">
            Your Code
          </p>
          <button
            onClick={handleCopy}
            className="w-full flex items-center gap-2 text-left"
          >
            <Sparkles className="w-3 h-3 text-primary-400/60 shrink-0" />
            <code className="text-xs font-mono text-text-primary tracking-wider flex-1">
              {stellrCode}
            </code>
            {copied ? (
              <Check className="w-3 h-3 text-status-available shrink-0" />
            ) : (
              <Copy className="w-3 h-3 text-text-muted/50 hover:text-primary-400 transition-colors shrink-0" />
            )}
          </button>
        </div>
      )}

      {/* Brand copy */}
      <div className="mx-4 mb-5 px-3.5 py-3 rounded-xl bg-gradient-to-br from-primary-500/6 to-accent-500/4 border border-white/[0.04]">
        <p className="text-[11px] leading-relaxed text-text-muted/70">
          Your time is valuable.
          <br />
          Spend it with the right people.
        </p>
      </div>
    </aside>
  );
}
