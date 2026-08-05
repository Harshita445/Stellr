"use client";

import { useState, useEffect, useRef } from "react";
import { Search, X, Star, ChevronDown } from "lucide-react";
import { api, FriendSearchResult, FriendRelation } from "@/lib/api-client";
import { Input } from "@/components/ui/input";

interface FriendPickerProps {
  currentUserId: string;
  onPeopleChange?: (people: FriendSearchResult[]) => void;
}

export function FriendPicker({ currentUserId, onPeopleChange }: FriendPickerProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<FriendSearchResult[]>([]);
  const [selected, setSelected] = useState<FriendSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [existingFriends, setExistingFriends] = useState<Set<string>>(new Set());

  const [showCodeInput, setShowCodeInput] = useState(false);
  const [codeQuery, setCodeQuery] = useState("");
  const [codeResult, setCodeResult] = useState<FriendSearchResult | null>(null);
  const [codeLoading, setCodeLoading] = useState(false);
  const [codeError, setCodeError] = useState<string | null>(null);

  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    api.friends.list()
      .then((data) => setExistingFriends(new Set(data.friends.map((f: FriendRelation) => f.user.id))))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (query.length < 3) {
      setResults([]);
      setSearched(false);
      return;
    }
    clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      setLoading(true);
      setSearched(true);
      try {
        const data = await api.friends.search(query);
        setResults(data.filter((r) => r.id !== currentUserId));
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer.current);
  }, [query, currentUserId]);

  function addPerson(person: FriendSearchResult) {
    if (selected.find((s) => s.id === person.id)) return;
    const next = [...selected, person];
    setSelected(next);
    onPeopleChange?.(next);
    if (existingFriends.has(person.id)) return;
    api.friends.add(person.id).catch(() => {});
  }

  function removePerson(id: string) {
    const next = selected.filter((s) => s.id !== id);
    setSelected(next);
    onPeopleChange?.(next);
  }

  async function searchByCode() {
    if (codeQuery.length < 4) return;
    setCodeLoading(true);
    setCodeError(null);
    setCodeResult(null);
    try {
      const data = await api.friends.searchByCode(codeQuery);
      if (data.length === 0 || data[0].id === currentUserId) {
        setCodeError("No user found with that code");
      } else {
        setCodeResult(data[0]);
      }
    } catch {
      setCodeError("Could not find that code");
    } finally {
      setCodeLoading(false);
    }
  }

  const allSelected = new Set(selected.map((s) => s.id));

  return (
    <div className="space-y-3">
      {selected.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {selected.map((p) => (
            <div
              key={p.id}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-space-700/70 border border-space-400/30"
            >
              <Star className="w-3 h-3 text-primary-400 fill-primary-400/30" />
              <span className="text-xs text-text-primary">{p.display_name}</span>
              <button
                onClick={() => removePerson(p.id)}
                className="text-text-muted hover:text-text-primary transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name..."
          className="pl-10 pr-8"
        />
        {query && (
          <button
            onClick={() => { setQuery(""); setResults([]); setSearched(false); }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Search results */}
      {loading && (
        <div className="space-y-2">
          {[1, 2].map((i) => (
            <div key={i} className="flex items-center gap-3 p-2.5">
              <div className="w-8 h-8 rounded-full bg-white/[0.04] animate-pulse" />
              <div className="flex-1 h-4 bg-white/[0.04] rounded animate-pulse" />
            </div>
          ))}
        </div>
      )}
      {!loading && searched && results.length === 0 && query.length >= 3 && (
        <p className="text-xs text-text-muted text-center py-2">No results found</p>
      )}
      {!loading && results.length > 0 && (
        <div className="space-y-1 max-h-40 overflow-y-auto">
          {results.map((person) => (
            <button
              key={person.id}
              type="button"
              onClick={() => addPerson(person)}
              disabled={allSelected.has(person.id)}
              className="w-full flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/[0.04] disabled:opacity-40 disabled:pointer-events-none transition-colors text-left"
            >
              <div className="w-8 h-8 rounded-full bg-primary-500/15 flex items-center justify-center text-primary-400 text-xs font-semibold shrink-0">
                {person.display_name.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary truncate">{person.display_name}</p>
                {person.section_code && (
                  <p className="text-xs text-text-muted">{person.section_code}</p>
                )}
              </div>
              {allSelected.has(person.id) && (
                <CheckIcon />
              )}
            </button>
          ))}
        </div>
      )}

      {/* Stellr code toggle */}
      <div className="text-center">
        <button
          type="button"
          onClick={() => setShowCodeInput(!showCodeInput)}
          className="text-xs text-primary-400 hover:text-primary-300 transition-colors inline-flex items-center gap-1"
        >
          Have someone&apos;s Stellr code?
          <ChevronDown className={`w-3 h-3 transition-transform ${showCodeInput ? "rotate-180" : ""}`} />
        </button>
      </div>

      {showCodeInput && (
        <div className="space-y-2">
          <div className="flex gap-2">
            <input
              value={codeQuery}
              onChange={(e) => setCodeQuery(e.target.value.toUpperCase())}
              placeholder="e.g. JANE-A3K9"
              className="flex-1 bg-space-700/50 border border-space-400/30 rounded-lg px-3 py-2 text-xs text-text-primary placeholder:text-text-muted/50 focus:outline-none focus:ring-1 focus:ring-primary-500/30 uppercase"
              onKeyDown={(e) => { if (e.key === "Enter") searchByCode(); }}
            />
            <button
              type="button"
              onClick={searchByCode}
              disabled={codeLoading || codeQuery.length < 4}
              className="px-3 py-2 rounded-lg bg-primary-600 text-white text-xs font-medium hover:bg-primary-500 disabled:opacity-40 transition-colors"
            >
              {codeLoading ? "..." : "Add"}
            </button>
          </div>
          {codeError && <p className="text-xs text-status-busy">{codeError}</p>}
          {codeResult && (
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.06]">
              <div className="flex items-center gap-2">
                <Star className="w-3.5 h-3.5 text-primary-400 fill-primary-400/30" />
                <span className="text-xs text-text-primary">{codeResult.display_name}</span>
              </div>
              <button
                type="button"
                onClick={() => addPerson(codeResult)}
                disabled={allSelected.has(codeResult.id)}
                className="text-xs text-primary-400 hover:text-primary-300 disabled:opacity-40 disabled:pointer-events-none"
              >
                {allSelected.has(codeResult.id) ? "Added" : "Add"}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function CheckIcon() {
  return (
    <svg className="w-4 h-4 text-primary-400" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" />
      <path d="M5 8.5L7 10.5L11 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
