"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { Check, ChevronDown, Search } from "lucide-react";
import { api, SectionItem } from "@/lib/api-client";

interface SectionComboboxProps {
  value: string | null;
  onChange: (code: string) => void;
}

export function SectionCombobox({ value, onChange }: SectionComboboxProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [sections, setSections] = useState<SectionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.sections.list()
      .then((data) => setSections(data.sections))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(
    () =>
      query.length < 1
        ? sections
        : sections.filter(
            (s) =>
              s.name.toLowerCase().includes(query.toLowerCase()) ||
              s.department.toLowerCase().includes(query.toLowerCase()),
          ),
    [sections, query],
  );

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const selectedLabel = value ? sections.find((s) => s.name === value) : null;

  return (
    <div ref={containerRef} className="relative">
      <label className="text-xs text-text-muted block mb-1.5">Section</label>
      <button
        type="button"
        className="w-full flex items-center justify-between bg-space-700/50 border border-space-400/30 rounded-lg px-4 py-2.5 text-sm text-left text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500/50 transition-all duration-200"
        onClick={() => { setOpen(!open); setQuery(""); setTimeout(() => inputRef.current?.focus(), 50); }}
      >
        <span className={value ? "text-text-primary" : "text-text-muted/50"}>
          {value || "Select a section..."}
        </span>
        <ChevronDown className={`w-4 h-4 text-text-muted transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="absolute z-20 left-0 right-0 top-full mt-1 glass-strong rounded-xl border border-white/[0.08] shadow-xl overflow-hidden">
          <div className="p-2 border-b border-white/[0.06]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-text-muted" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Filter sections..."
                className="w-full bg-space-700/50 border border-space-400/20 rounded-lg pl-9 pr-3 py-2 text-xs text-text-primary placeholder:text-text-muted/50 focus:outline-none focus:ring-1 focus:ring-primary-500/30"
              />
            </div>
          </div>
          <div className="max-h-48 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-xs text-text-muted">Loading...</div>
            ) : filtered.length === 0 ? (
              <div className="p-4 text-center text-xs text-text-muted">No sections found</div>
            ) : (
              filtered.map((s) => (
                <button
                  key={s.name}
                  type="button"
                  className="w-full flex items-center gap-2 px-4 py-2.5 text-xs text-left text-text-secondary hover:bg-white/[0.04] hover:text-text-primary transition-colors"
                  onClick={() => {
                    onChange(s.name);
                    setOpen(false);
                    setQuery("");
                  }}
                >
                  <div className={`w-4 h-4 rounded-full border flex items-center justify-center shrink-0 ${
                    value === s.name
                      ? "border-primary-400 bg-primary-500/20"
                      : "border-space-300"
                  }`}>
                    {value === s.name && <Check className="w-3 h-3 text-primary-400" />}
                  </div>
                  <span className="font-medium">{s.name}</span>
                  <span className="text-text-muted ml-auto">{s.department}</span>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
