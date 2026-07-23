"use client";

import { useState, useEffect, useCallback } from "react";
import { Star, UserPlus, UserMinus } from "lucide-react";
import { api, FriendRelation } from "@/lib/api-client";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

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
    } catch (err) {
      setError("Could not load friends");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFriends();
  }, [loadFriends]);

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
      <Card>
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
      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-accent-400" />
              Visible Stars
            </div>
          </CardTitle>
        </CardHeader>
        <p className="text-sm text-status-busy">{error}</p>
      </Card>
    );
  }

  if (friends.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-accent-400" />
              Visible Stars
            </div>
          </CardTitle>
        </CardHeader>
        <div className="flex flex-col items-center gap-2 py-6 text-text-muted">
          <Star className="w-8 h-8 opacity-30" />
          <p className="text-sm">No stars yet</p>
          <p className="text-xs text-text-muted/60">
            Search for classmates to add them as stars
          </p>
          <a
            href="/friends"
            className="inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 px-4 py-2 text-sm gap-2 glass text-text-primary hover:bg-white/10 active:bg-white/15"
          >
            <UserPlus className="w-4 h-4" />
            Find Stars
          </a>
        </div>
      </Card>
    );
  }

  return (
    <Card>
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
        {friends.map((fr) => (
          <div
            key={fr.id}
            className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors group"
          >
            <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-400 text-sm font-semibold shrink-0">
              {fr.user.display_name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-text-primary truncate">
                {fr.user.display_name}
              </p>
              {fr.user.section_code && (
                <p className="text-xs text-text-muted">{fr.user.section_code}</p>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleRemove(fr.user.id)}
              className="opacity-0 group-hover:opacity-100"
            >
              <UserMinus className="w-4 h-4" />
            </Button>
          </div>
        ))}
      </div>
    </Card>
  );
}
