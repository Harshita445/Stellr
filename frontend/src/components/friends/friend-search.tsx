"use client";

import { useState, useEffect, useRef } from "react";
import { Search, UserPlus, UserMinus, Users, X } from "lucide-react";
import { api, FriendSearchResult } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface FriendSearchProps {
  existingFriendIds: Set<string>;
  onAdd: (userId: string) => void;
  onRemove: (userId: string) => void;
}

export function FriendSearch({ existingFriendIds, onAdd, onRemove }: FriendSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<FriendSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

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
        setResults(data);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer.current);
  }, [query]);

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search classmates by name..."
          className="pl-10 pr-8"
        />
        {query && (
          <button
            onClick={() => setQuery("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400 rounded"
            aria-label="Clear search"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-3 p-3">
              <Skeleton className="w-10 h-10 rounded-full" />
              <div className="flex-1 space-y-1.5">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-20" />
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && searched && results.length === 0 && (
        <div className="flex flex-col items-center gap-2 py-8 text-text-muted">
          <Users className="w-8 h-8 opacity-40" />
          <p className="text-sm">No classmates found</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="space-y-2">
          {results.map((user) => {
            const isFriend = existingFriendIds.has(user.id);
            return (
              <Card key={user.id} className="flex items-center gap-3 p-3">
                <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-400 text-sm font-semibold shrink-0">
                  {user.display_name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">
                    {user.display_name}
                  </p>
                  {user.section_code && (
                    <p className="text-xs text-text-muted">{user.section_code}</p>
                  )}
                </div>
                {isFriend ? (
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => onRemove(user.id)}
                  >
                    <UserMinus className="w-4 h-4" />
                    Remove
                  </Button>
                ) : (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => onAdd(user.id)}
                  >
                    <UserPlus className="w-4 h-4" />
                    Add
                  </Button>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
