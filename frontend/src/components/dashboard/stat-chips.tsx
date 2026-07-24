"use client";

import { Clock, BookOpen, Users, Target } from "lucide-react";

interface StatChipProps {
  icon: React.ElementType;
  label: string;
  value: string;
  accent?: string;
}

function StatChip({ icon: Icon, label, value, accent }: StatChipProps) {
  return (
    <div className="flex-1 min-w-0 flex items-center gap-3 px-4 py-2.5 rounded-xl glass border border-white/[0.06]">
      <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${
        accent === "green" ? "bg-status-available/20" :
        accent === "purple" ? "bg-primary-500/20" :
        accent === "blue" ? "bg-accent-400/20" :
        accent === "amber" ? "bg-status-away/20" :
        "bg-white/[0.04]"
      }`}>
        <Icon className={`w-4 h-4 ${
          accent === "green" ? "text-status-available" :
          accent === "purple" ? "text-primary-400" :
          accent === "blue" ? "text-accent-400" :
          accent === "amber" ? "text-status-away" :
          "text-text-muted"
        }`} />
      </div>
      <div className="min-w-0">
        <p className="text-[11px] text-text-muted leading-tight truncate">{label}</p>
        <p className={`text-sm font-semibold truncate ${
          accent === "green" ? "text-status-available" : "text-text-primary"
        }`}>
          {value}
        </p>
      </div>
    </div>
  );
}

export function StatChips() {
  return (
    <div className="flex gap-3">
      <StatChip icon={Clock} label="Status" value="You're free" accent="green" />
      <StatChip icon={BookOpen} label="Next class" value="DBMS at 13:30" accent="purple" />
      <StatChip icon={Users} label="People free now" value="0" accent="blue" />
      <StatChip icon={Target} label="Next alignment" value="—" accent="amber" />
    </div>
  );
}
