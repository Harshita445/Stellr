"use client";

import { useState, useEffect, useCallback } from "react";
import { Clock, Users } from "lucide-react";
import { api, FriendRelation, AvailabilityResponse } from "@/lib/api-client";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function NextAlignment() {
  const [friends, setFriends] = useState<FriendRelation[]>([]);
  const [loadingFriends, setLoadingFriends] = useState(true);
  const [availByFriend, setAvailByFriend] = useState<Record<string, AvailabilityResponse>>({});
  const [loadingAvail, setLoadingAvail] = useState(false);

  const loadFriends = useCallback(async () => {
    try {
      setLoadingFriends(true);
      const data = await api.friends.list();
      setFriends(data.friends);
    } catch {
      // handled
    } finally {
      setLoadingFriends(false);
    }
  }, []);

  useEffect(() => {
    loadFriends();
  }, [loadFriends]);

  useEffect(() => {
    if (friends.length === 0) {
      setLoadingAvail(false);
      return;
    }
    setLoadingAvail(true);
    let cancelled = false;
    Promise.all(
      friends.map(async (fr) => {
        try {
          const result = await api.availability.compareFriend(fr.user.id);
          if (!cancelled) {
            setAvailByFriend((prev) => ({ ...prev, [fr.user.id]: result }));
          }
        } catch {
          // skip
        }
      }),
    ).finally(() => {
      if (!cancelled) setLoadingAvail(false);
    });
    return () => { cancelled = true; };
  }, [friends]);

  const hasAvailability = Object.keys(availByFriend).length > 0;

  if (loadingFriends) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-accent-400" />
              Next Alignment
            </div>
          </CardTitle>
        </CardHeader>
        <Skeleton className="h-16 rounded-lg" />
      </Card>
    );
  }

  if (friends.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-accent-400" />
            Next Alignment
          </div>
        </CardTitle>
      </CardHeader>

      {loadingAvail && !hasAvailability ? (
        <Skeleton className="h-16 rounded-lg" />
      ) : (
        <div className="space-y-2">
          {friends.map((fr) => {
            const avail = availByFriend[fr.user.id];
            const next = avail?.next_slot;
            const now = avail?.current_overlap;
            return (
              <div
                key={fr.user.id}
                className="flex items-center gap-3 p-2 rounded-lg"
              >
                <div className="w-8 h-8 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-400 text-xs font-semibold shrink-0">
                  {fr.user.display_name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">
                    {fr.user.display_name}
                  </p>
                  {avail && (
                    <p className="text-xs text-text-muted">
                      {now ? (
                        <span className="text-status-free">Free now</span>
                      ) : next ? (
                        <>Next: {next.start} – {next.end}</>
                      ) : (
                        "No overlap today"
                      )}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
          {!loadingAvail && !hasAvailability && (
            <div className="flex items-center gap-2 py-3 text-text-muted text-sm">
              <Users className="w-4 h-4 opacity-30" />
              <span>Loading availability data...</span>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
