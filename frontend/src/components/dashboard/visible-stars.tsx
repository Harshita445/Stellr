"use client";

import { useState, useEffect, useCallback } from "react";
import { Star, UserPlus, UserMinus, AlertCircle } from "lucide-react";
import { api, FriendRelation } from "@/lib/api-client";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

function useFriendAvailabilities(friends: FriendRelation[]) {
  const [availMap, setAvailMap] = useState<Map<string, boolean>>(new Map());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (friends.length === 0) {
      setAvailMap(new Map());
      return;
    }

    let cancelled = false;
    const fetchAll = async () => {
      setLoading(true);
      const map = new Map<string, boolean>();
      const results = await Promise.allSettled(
        friends.map((fr) => api.availability.compareFriend(fr.user.id)),
      );
      friends.forEach((fr, i) => {
        const r = results[i];
        if (r.status === "fulfilled") {
          map.set(fr.user.id, r.value.current_overlap);
        } else {
          map.set(fr.user.id, false);
        }
      });
      if (!cancelled) {
        setAvailMap(map);
        setLoading(false);
      }
    };

    fetchAll();

    const interval = setInterval(fetchAll, 60000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [friends]);

  return { availMap, loading };
}

export function VisibleStars() {
  const [friends, setFriends] = useState<FriendRelation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadFriends = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.friends.list();
      setFriends(data.friends);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Could not load friends";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFriends();
  }, [loadFriends]);

  const { availMap } = useFriendAvailabilities(friends);

  const handleRemove = async (userId: string) => {
    const prev = [...friends];
    setFriends((f) => f.filter((fr) => fr.user.id !== userId));
    try {
      await api.friends.remove(userId);
    } catch {
      setFriends(prev);
    }
  };

  if (loading) {
    return (
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(139,92,246,0.03)_0%,transparent_60%)] pointer-events-none" />
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-accent-400" />
              Visible Stars
            </div>
          </CardTitle>
        </CardHeader>
        <div className="space-y-3">
          {[1, 2].map((i) => (
            <div key={i} className="flex items-center gap-3">
              <Skeleton className="w-10 h-10 rounded-full" />
              <div className="flex-1 space-y-1.5">
                <Skeleton className="h-4 w-28" />
                <Skeleton className="h-3 w-16" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(239,68,68,0.03)_0%,transparent_60%)] pointer-events-none" />
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-accent-400" />
              Visible Stars
            </div>
          </CardTitle>
        </CardHeader>
        <div className="flex flex-col items-center gap-3 py-6 text-center">
          <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
            <AlertCircle className="w-6 h-6 text-red-400" />
          </div>
          <p className="text-sm text-red-400">{error}</p>
          <Button variant="secondary" size="sm" onClick={loadFriends}>
            Try again
          </Button>
        </div>
      </Card>
    );
  }

  if (friends.length === 0) {
    return (
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(139,92,246,0.03)_0%,transparent_60%)] pointer-events-none" />
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-8 right-8 w-2 h-2 rounded-full bg-primary-400/10" />
          <div className="absolute bottom-12 left-6 w-1.5 h-1.5 rounded-full bg-accent-400/8" />
          <div className="absolute top-1/3 left-1/4 w-1 h-1 rounded-full bg-primary-400/6" />
          <div className="absolute bottom-1/3 right-1/4 w-1.5 h-1.5 rounded-full bg-accent-400/6" />
        </div>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-accent-400" />
              Visible Stars
            </div>
          </CardTitle>
        </CardHeader>
        <div className="flex flex-col items-center gap-4 py-10 text-center relative">
          <div className="w-16 h-16 rounded-full bg-primary-500/8 flex items-center justify-center">
            <Star className="w-8 h-8 text-primary-400/40" />
          </div>
          <div>
            <p className="text-base font-semibold text-text-primary">
              No stars in your sky yet
            </p>
            <p className="text-sm text-text-muted mt-1 max-w-xs">
              Add friends by searching their roll number to start connecting
            </p>
          </div>
          <div className="flex flex-col items-center gap-2">
            <a
              href="/friends"
              className="inline-flex items-center justify-center rounded-lg font-semibold text-sm transition-all duration-200 h-10 px-5 gap-2 bg-primary-600 text-white hover:bg-primary-500 active:bg-primary-700 shadow-glow-sm hover:shadow-glow-md"
            >
              <UserPlus className="w-4 h-4" />
              Find Stars
            </a>
            <p className="text-xs text-text-muted/60">
              or create a Constellation with friends later
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(139,92,246,0.03)_0%,transparent_60%)] pointer-events-none" />
      <CardHeader>
        <CardTitle>
          <div className="flex items-center gap-2">
            <Star className="w-4 h-4 text-accent-400" />
            Visible Stars
            <span className="text-xs font-normal text-text-muted ml-1">
              ({friends.length})
            </span>
          </div>
        </CardTitle>
      </CardHeader>
      <div className="space-y-2">
        {friends.map((fr) => {
          const isFree = availMap.get(fr.user.id) ?? false;
          return (
            <div
              key={fr.id}
              className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/[0.06] transition-colors group"
            >
              <div className="relative shrink-0">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold transition-shadow duration-300 ${
                    isFree
                      ? "bg-status-available/15 text-status-available shadow-[0_0_12px_rgba(34,197,94,0.2)]"
                      : "bg-space-400/30 text-text-muted"
                  }`}
                >
                  {fr.user.display_name.charAt(0).toUpperCase()}
                </div>
                <span
                  className={`absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-space-900 ${
                    isFree
                      ? "bg-status-available shadow-[0_0_6px_rgba(34,197,94,0.5)]"
                      : "bg-space-400"
                  }`}
                />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary truncate">
                  {fr.user.display_name}
                </p>
                <p
                  className={`text-xs ${
                    isFree ? "text-status-available" : "text-text-muted"
                  }`}
                >
                  {isFree ? "Free now" : fr.user.section_code ?? "Busy"}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleRemove(fr.user.id)}
                className="opacity-0 group-hover:opacity-100"
                aria-label={`Remove ${fr.user.display_name}`}
              >
                <UserMinus className="w-4 h-4" />
              </Button>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
